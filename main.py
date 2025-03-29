from elasticsearch import Elasticsearch

import argparse
import sys
import time

def parse_args():
    parser = argparse.ArgumentParser(description="Reindex Elasticsearch index with lowercase field names.")
    parser.add_argument("-i", "--index", required=True, help="Source index name")
    parser.add_argument("-o", "--output-index", help="Destination index name (optional)")
    parser.add_argument("-hs", "--host", default="http://localhost:9200", help="Elasticsearch host (default: http://localhost:9200)")
    parser.add_argument("--keep-original", action="store_true", help="Do not delete the original index or create alias")
    return parser.parse_args()

def connect(host):
    for attempt in range(1, 6):
        try:
            es = Elasticsearch(host)
            if es.ping():
                print(f"[ELSTC] Connected to Elasticsearch at {host}")
                return es
        except Exception as e:
            print(f"[ERROR] Connection attempt {attempt} failed: {e}")
        print(f"[ELSTC] Retrying in 3 seconds...")
        time.sleep(3)

    print("[FATAL] Could not connect to Elasticsearch after multiple attempts.")
    sys.exit(1)

def exists(es, index):
    return es.indices.exists(index=index)

def settings(es, index):
    settings = es.indices.get_settings(index=index)[index]['settings']['index']
    for field in ['uuid', 'version', 'creation_date', 'provided_name']:
        settings.pop(field, None)
    return settings

def create(es, index, settings):
    body = {
        "settings": settings,
        "mappings": {
            "dynamic": True
        }
    }
    try:
        es.indices.create(index=index, body=body)
        print(f"[ELSTC] Created index: {index}")
    except Exception as e:
        print(f"[ERROR] Failed to create index '{index}': {e.info}")
        sys.exit(1)

def reindex_with_lowercase(es, source_index, dest_index):
    script = """
        Map sourceClone = new HashMap(ctx._source);
        ctx._source.clear();
        for (entry in sourceClone.entrySet()) {
            ctx._source.put(entry.getKey().toLowerCase(), entry.getValue());
        }
    """
    body = {
        "source": {"index": source_index},
        "dest": {"index": dest_index},
        "script": {
            "lang": "painless",
            "source": script
        }
    }
    try:
        es.options(request_timeout=600).reindex(body=body, wait_for_completion=True)
        print("[ELSTC] Reindexing completed with lowercase field transformation.")
    except Exception as e:
        print(f"[ERROR] Reindexing failed: {e.info}")
        sys.exit(1)

def count_docs(es, index):
    return es.count(index=index)['count']

def delete(es, index):
    try:
        es.indices.delete(index=index)
        print(f"[ELSTC] Deleted index: {index}")
    except Exception as e:
        print(f"[WARNING] Tried to delete non-existing index: {index}")

def create_alias(es, alias_name, index):
    try:
        es.indices.update_aliases(body={
            "actions": [
                { "add": { "index": index, "alias": alias_name } }
            ]
        })
        print(f"[ELSTC] Alias '{alias_name}' now points to '{index}'")
    except Exception as e:
        print(f"[ERROR] Failed to create alias: {str(e)}")
        sys.exit(1)

def main():
    args = parse_args()

    src_index = args.index
    dst_index = args.output_index or f"{src_index}_lowercase"
    delete_original = not args.keep_original and args.output_index is not None and args.output_index != args.index

    es = connect(args.host)

    if not exists(es, src_index):
        print(f"[ERROR] Source index '{src_index}' does not exist.")
        sys.exit(1)

    create(es, dst_index, settings(es, src_index))

    print(f"[ELSTC] Reindexing from '{src_index}' to '{dst_index}' with lowercase transformation...")
    reindex_with_lowercase(es, src_index, dst_index)

    es.indices.refresh(index=dst_index)

    src_count = count_docs(es, src_index)
    dst_count = count_docs(es, dst_index)

    print(f"[ELSTC] Document count — Source: {src_count}, Destination: {dst_count}")
    if src_count != dst_count:
        print("[WARNING] Document count mismatch detected.")

    if delete_original:
        print(f"[ELSTC] Deleting original index '{src_index}'...")
        delete(es, src_index)

        print(f"[ELSTC] Creating alias '{src_index}' -> '{dst_index}'...")
        create_alias(es, src_index, dst_index)

    print("\n[SUMMARY]")
    print(f"  Reindex complete  : Yes")
    print(f"  Source index      : {src_index}")
    print(f"  Destination index : {dst_index}")
    print(f"  Alias created     : {'Yes' if delete_original else 'No'}")
    print(f"  Original deleted  : {'Yes' if delete_original else 'No'}")
    print(f"  Document count    : {dst_count}")

if __name__ == "__main__":
    main()
