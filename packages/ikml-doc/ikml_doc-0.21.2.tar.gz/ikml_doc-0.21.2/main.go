package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"html"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

const indent = 2

// Node represents a node in our tree.
type Node struct {
	RawData  string
	TagName  string
	Content  string
	Props    map[string]string
	Parent   *Node
	Children []*Node
}

// NewNode creates a new Node from a raw line of IKML.
func NewNode(rawData string, parent *Node) (*Node, error) {
	if strings.TrimSpace(rawData) == "" {
		return nil, fmt.Errorf("empty data: cannot create node")
	}
	tagName, core, content := parseIKMLNode(rawData)
	props := parseProps(core)
	node := &Node{
		RawData: rawData,
		TagName: tagName,
		Content: content,
		Props:   props,
		Parent:  parent,
	}
	if parent != nil {
		parent.Children = append(parent.Children, node)
	}
	return node, nil
}

func parseIKMLNode(line string) (string, string, string) {
	// Expecting a format like: [tag props] content
	// Split the line into the bracketed part and the content.
	parts := strings.SplitN(line, "]", 2)
	if len(parts) < 2 {
		return "", "", ""
	}
	core := strings.TrimSpace(parts[0] + "]")
	// Unescape the HTML entities in the content portion.
	content := strings.TrimSpace(html.UnescapeString(parts[1]))

	// Use regex to extract the tag name from the core part.
	reTag := regexp.MustCompile(`\[[ ]*([.A-Za-z]+)`)
	match := reTag.FindStringSubmatch(core)
	tagName := ""
	if len(match) >= 2 {
		tagName = strings.TrimSpace(match[1])
	}
	return tagName, core, content
}

func parseProps(core string) map[string]string {
	props := make(map[string]string)

	// Extract key="value" or key='value' pairs.
	reQuoted := regexp.MustCompile(`([A-Za-z]+)=["'](.*?)["']`)
	quotedMatches := reQuoted.FindAllStringSubmatch(core, -1)
	for _, match := range quotedMatches {
		if len(match) >= 3 {
			props[match[1]] = match[2]
		}
	}

	// Replace quoted texts with a placeholder.
	coreWOQ := regexp.MustCompile(`["'].*?["']`).ReplaceAllString(core, "<!!>")

	// Extract key=value pairs (without quotes) ending with space or ']' character.
	reUnquoted := regexp.MustCompile(`([A-Za-z]+)=([^ \]]+)[ \]]`)
	unquotedMatches := reUnquoted.FindAllStringSubmatch(coreWOQ, -1)
	for _, match := range unquotedMatches {
		if len(match) >= 3 && match[2] != "<!!>" {
			props[match[1]] = match[2]
		}
	}

	return props
}

// ToString writes the node (and its children) as a text tree.
func (n *Node) ToString(excludeRoot bool, quotedAttr bool, maxDepth int) string {
	var b strings.Builder
	n.writeToBuffer(&b, 0, excludeRoot, quotedAttr, maxDepth)
	return b.String()
}

func (n *Node) writeToBuffer(b *strings.Builder, depth int, excludeRoot bool, quotedAttr bool, maxDepth int) {
	if maxDepth >= 0 && depth > maxDepth {
		return
	}
	if !(depth == 0 && excludeRoot) {
		prefix := strings.Repeat(" ", depth*indent)
		b.WriteString(prefix)
		b.WriteString(n.String(quotedAttr))
		b.WriteString("\n")
	}
	if depth == 0 && excludeRoot {
		depth -= 1
	}

	for _, child := range n.Children {
		child.writeToBuffer(b, depth+1, false, quotedAttr, maxDepth)
	}
}

// String returns a string representation of the node.
func (n *Node) String(quotedAttr bool) string {
	var parts []string
	parts = append(parts, n.TagName)
	// In this example we sort keys alphabetically except a fixed order on "id" and "rel_id".
	// For simplicity, we output id and rel_id first if present.
	if val, ok := n.Props["id"]; ok {
		if quotedAttr {
			parts = append(parts, fmt.Sprintf(`id="%s"`, val))
		} else {
			parts = append(parts, fmt.Sprintf("id=%s", val))
		}
	}
	if val, ok := n.Props["rel_id"]; ok {
		if quotedAttr {
			parts = append(parts, fmt.Sprintf(`rel_id="%s"`, val))
		} else {
			parts = append(parts, fmt.Sprintf("rel_id=%s", val))
		}
	}
	// Append remaining keys.
	for k, v := range n.Props {
		if k == "id" || k == "rel_id" {
			continue
		}
		if quotedAttr {
			parts = append(parts, fmt.Sprintf(`%s="%s"`, k, v))
		} else {
			parts = append(parts, fmt.Sprintf("%s=%s", k, v))
		}
	}
	// Build a tag string similar to IKML
	return fmt.Sprintf("[%s] %s", strings.Join(parts, " "), n.Content)
}

// ikmlToTree converts IKML data lines into a tree.
func ikmlToTree(ikmlLines []string) *Node {
	root, _ := NewNode("[root]", nil)
	// We'll use a stack to track the tree levels.
	parentsStack := []*Node{root}
	currentLevel := -1
	var prevNode *Node = root

	for _, line := range ikmlLines {
		// Skip empty/commented lines.
		trimmedLine := strings.Split(line, "#")[0]
		if strings.TrimSpace(trimmedLine) == "" {
			continue
		}
		// count leading spaces until first "[" appears.
		tindent := strings.Index(trimmedLine, "[")
		if tindent < 0 {
			continue
		}
		newLevel := tindent / indent
		// Adjust stack based on level.
		if newLevel > currentLevel {
			parentsStack = append(parentsStack, prevNode)
		} else if newLevel < currentLevel {
			for currentLevel > newLevel {
				if len(parentsStack) > 0 {
					parentsStack = parentsStack[:len(parentsStack)-1]
				}
				currentLevel--
			}
		}
		parent := parentsStack[len(parentsStack)-1]
		node, err := NewNode(strings.TrimSpace(trimmedLine), parent)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error creating node from line: %s. Error: %v\n", trimmedLine, err)
			continue
		}
		prevNode = node
		currentLevel = newLevel
	}

	return root
}

// toDict returns a map representation of the tree.
func (n *Node) toDict(maxDepth int, depth int) map[string]interface{} {
	out := make(map[string]interface{})
	out["tag_name"] = n.TagName
	out["content"] = n.Content
	for k, v := range n.Props {
		out[k] = v
	}
	children := []map[string]interface{}{}
	if maxDepth < 0 || depth < maxDepth {
		for _, child := range n.Children {
			children = append(children, child.toDict(maxDepth, depth+1))
		}
	}
	out["children"] = children
	return out
}

// toJSON returns the tree as a JSON string.
func (n *Node) toJSON(maxDepth int) (string, error) {
	dict := n.toDict(maxDepth, 0)
	j, err := json.MarshalIndent(dict, "", "  ")
	if err != nil {
		return "", err
	}
	return string(j), nil
}

// treeAsXML returns the tree as an XML string list.
func (n *Node) treeAsXML(maxDepth int, depth int) []string {
	var lines []string
	if maxDepth >= 0 && depth > maxDepth {
		return lines
	}
	openTag := openXMLTag(n.String(true))
	closeTag := closeXMLTag(n.String(true))
	lines = append(lines, openTag)
	for _, child := range n.Children {
		lines = append(lines, child.treeAsXML(maxDepth, depth+1)...)
	}
	lines = append(lines, closeTag)
	return lines
}

func openXMLTag(tagline string) string {
	// For simplicity, replace leading "[" with "<" and trailing "]" with ">".
	tagline = strings.TrimSpace(tagline)
	if strings.HasPrefix(tagline, "[") && strings.Contains(tagline, "]") {
		return strings.Replace(strings.SplitN(tagline, "]", 2)[0], "[", "<", 1) + ">"
	}
	return "<" + tagline + ">"
}

func closeXMLTag(tagline string) string {
	// Use the tagName extracted from the tagline.
	tagName := ""
	parts := strings.SplitN(tagline, "]", 2)
	if len(parts) > 0 {
		tagPart := parts[0]
		tagPart = strings.TrimPrefix(tagPart, "[")
		tagName = strings.Fields(tagPart)[0]
	}
	return fmt.Sprintf("</%s>", tagName)
}

func readLinesFromFile(filename string) ([]string, error) {
	file, err := os.Open(filepath.Clean(filename))
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var lines []string
	reader := bufio.NewReader(file)
	for {
		line, err := reader.ReadString('\n')
		line = strings.TrimRight(line, "\r\n")
		if len(line) > 0 {
			lines = append(lines, line)
		}
		if err == io.EOF {
			break
		} else if err != nil {
			return lines, err
		}
	}
	return lines, nil
}

func usage(prog string) {
	fmt.Printf("Usage: %s input_ikml_file.txt\n", prog)
}

func main() {
	if len(os.Args) < 2 {
		usage(os.Args[0])
		return
	}
	inputFile := os.Args[1]
	lines, err := readLinesFromFile(inputFile)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading file: %v\n", err)
		return
	}
	root := ikmlToTree(lines)
	// For demonstration, we print the tree as text.
	fmt.Println(root.ToString(false, true, -1))

	// Uncomment the following to print the JSON representation:

	// jsonStr, err := root.toJSON(-1)
	// if err != nil {
	// 	fmt.Fprintf(os.Stderr, "Error converting to JSON: %v\n", err)
	// } else {
	// 	fmt.Println(jsonStr)
	// }

	// Uncomment the following to print an XML representation:

	// xmlLines := root.treeAsXML(-1, 0)
	// for _, line := range xmlLines {
	// 	fmt.Println(line)
	// }

}
