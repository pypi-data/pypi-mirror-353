# ikml-doc

## IKML Document Parser

### Description
A parser for IKML (Indic Knowledge Markup Language)

### Installation
To install the IKML parser, use the following command:

```bash
pip install ikml_doc
```

### Usage
The IKML parser can be used to load IKML data from a URL or a local file, and then convert it into various formats such as JSON, XML, and plain text.

#### Loading IKML Data
You can load IKML data from a URL or a local file using the `IKML_Document` class.

```python
from ikml_doc import IKML_Document
```

```python
ikml_url = "https://api.siddhantakosha.org/ikmldata?expand_inline=1&gpath=libraries/smap-granthas/Tattvabodha/all-ikml.txt&fmt=txt"
```

```python
# Load from URL
doc = IKML_Document(url=ikml_url)

# Load from raw data (string or dict)
doc = IKML_Document(data="path_to_ikml.txt")
```

#### Saving Data
```python
def save(self, exclude_root=False, filename="out_ikml.txt")
```
- **Parameters**:
  - `exclude_root`: (bool) If `True`, the root node is excluded from the saved output.
  - `filename`: (string) The name of the file to save the IKML data.

Example:
```python
doc.save(filename="output_ikml.txt")
```

#### Converting Data
You can convert the loaded data into different formats.

- **To Dictionary**:
```python
doc_dict = doc.to_dict()
```

- **To JSON**:
```python
doc_json = doc.to_json()
```

- **To XML**:
```python
doc_xml = doc.to_xml(put_attrs_inside=True)
```

- **To Plain Text**:
```python
doc_txt = doc.to_txt(exclude_root=False, quoted_attr=False)
```

#### Iterating Over Nodes
You can iterate through the nodes using a generator method.

```python
for node in doc.iter():
    print("  "*node.depth, node)
```

#### Iterating Over Immediate Children

Use `node.children` to iterate over all child nodes. Use `node.node_children` to iterate over all child nodes that aren't attributes where `node.is_attribute` is `False`.

```python
for node in doc.iter():
    print("  "*node.depth, node)
    for child in node.children:
        print("  "*child.depth, child)
```

#### Finding Nodes
You can find nodes based on specific criteria.

- **Find Children by Tag Name**:
```python
for child in doc.find_children(tag_name="va"):
    print(child)
```

- **Get a Node by ID**:
```python
node = doc.get(tag_id="l.smaps.TatvB.v-1")
```

#### Accessing Attributes of Nodes
You can access attributes of the nodes directly.

- **Get Node Attributes**:
```python
attributes = node.keys()  # Get list of keys
value = node.get("id")  # Get value of a specific property
```

#### Validating Schema
You can validate the structure of the IKML document against a schema.

```python
schema_doc = IKML_Document(data=schema_data)
is_valid = doc.validate_schema(schema_doc)
```

---

### Example Usage

```python
from ikml_doc import IKML_Document

# Loading IKML data from a URL
ikml_url = "https://api.siddhantakosha.org/ikmldata?expand_inline=1&gpath=libraries/smap-granthas/Tattvabodha/all-ikml.txt&fmt=txt"
doc = IKML_Document(url=ikml_url)

# Iterating over all nodes
for i, node in enumerate(doc.iter()):
    node["new_attr_count"] = i

# Saving the loaded document
doc.save(filename="Tattvabodha_output.txt", exclude_root=True)

# Accessing a specific node and its properties
node = doc.get("l.smaps.TatvB.v-10")
print(node.keys())
print(node.get("new_attr_count"))
```


### Contributing
Contributions are welcome. Please open an issue to discuss any changes before submitting a pull request.

### License
This project is licensed under the LGPL License.

### Acknowledgments
Special thanks to the contributors and maintainers of the IKML project.
