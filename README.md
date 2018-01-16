# github-crawler
Simple Github crawler. 

### Input
Takes the input as a dictionary with search items needed, proxies to be used (picks one at random) and search type (supported are "Repositories", "Issues" and "Wikis") of the form e.g.
```
{
  "keywords": [
    "openstack",
    "nova",
    "css"
],
  "proxies": [
    "194.126.37.94:8080",
    "13.78.125.167:8080"
  ],
  "type": "Repositories"
}
```

### Output
Outputs of the form 
```
[
  {
    "url": "https://github.com/atuldjadhav/DropBox-Cloud-Storage",
    "extra": {
      "owner": "atuldjadhav",
      "language_stats": {
        "HTML": "0.8",
        "CSS": "52.0",
        "JavaScript": "47.2"
      }
    }
  }
]
```
for repo search. Wikis and Issues search only give the url. "extra" info can be disabled by switching switching off `extras` in `main()`.

### Testing and working mode
Two modes:

* testing (when `pytest = True` in `main()`) well-suited for pytest test coverage. Coverage results with the sample above have been attached to this repo under test_results.
* work (`pytest = False`) allows for usual command-line usage: `python3 test_crawler.py input.json` creates `results.json` file.
