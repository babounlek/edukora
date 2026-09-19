import json, sys
keys = set(sys.argv[2:])
recs = json.load(open("rendu_corpus_full.json", encoding="utf-8"))
sub = [r for r in recs if f"{r['model']}#{r['pk']}" in keys]
json.dump(sub, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False)
print(len(sub), "enregistrements")
