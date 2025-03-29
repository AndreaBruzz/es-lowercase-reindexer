# Elasticsearch Reindex with Lowercase Field Names

Have you ever indexed a ton of documents and then realized there's a "[best practice](https://www.elastic.co/guide/en/beats/devguide/current/event-conventions.html)" in Elasticsearch saying that field names should be lowercase? **No?** ...Well, I did. So I built this script to make my life easier by aligning my indices to that standard.

Basically, it takes an existing index, lowercases all the field names, and reindexes the data.  
You can choose to create a new index (if you're emotionally attached to your original one) or overwrite it with a fresh, lowercase-compliant version.

---

## Requirements

A running instance of Elasticsearch... Python... at least one index... and stop I think.
Oh, the elasticsearch package!

```bash
pip install elasticsearch
```

---

## Usage

Run the script like this:

```bash
python main.py -i <source_index> [-o <destination_index>] [--keep-original] [-hs <elasticsearch_host>]
```

### Options

- `-i` / `--index`: Source index name (required)
- `-o` / `--output-index`: Destination index name (optional)
- `--keep-original`: Prevent deletion of the original index and creation of an alias
- `-hs` / `--host`: Elasticsearch host (default: http://localhost:9200)

---

## Behavior Summary

| Scenario                       | Result                                                            |
| ------------------------------ | ----------------------------------------------------------------- |
| Only `-i` provided             | Reindexes to `<index>_lowercase`, deletes original, creates alias |
| `-i` and `-o` are the same     | Reindexes, keeps both indices, creates alias                      |
| `-i` and `-o` are different    | Reindexes to new index, deletes original, creates alias           |
| `--keep-original` is specified | Original index is preserved, no alias created                     |

---

## Try It Yourself!

### Step 1: Create a test index

Run:

```bash
python create_mock_index.py
```

---

### Step 2: Reindex with lowercase fields

```bash
python main.py -i mock_index
```

This will:

- Create `test_index_mixed_case_temp`
- Reindex documents with lowercase field names
- Delete the original index
- Create an alias so `mock_index` still works

---
