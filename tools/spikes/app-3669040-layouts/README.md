# App 3669040 layout enumerator

This standard-library Python tool queries the public SteamInputDB config-search
API once without a controller tag and once for every controller filter in
`controller-filters.json`. Each query uses the API maximum page size of 100 and
continues until the reported total has been consumed. Results are deduplicated
by Workshop `file_id`.

From the repository root:

```sh
python3 tools/spikes/app-3669040-layouts/enumerate_layouts.py \
  --inventory-output docs/spikes/app-3669040-controller-layouts/inventory.json \
  --evidence-output docs/spikes/app-3669040-controller-layouts/query-evidence.json
```

The tool treats `{}` as a successful zero-result response because the mapped Go
response omits zero `total` and empty `items`. It also fetches the app page and
records the server-rendered default-visible controller filters. The full filter
list is explicit because the page's additional filters appear only after the
client-side **Show More** interaction.

Run the tests with:

```sh
python3 -m unittest discover \
  -s tools/spikes/app-3669040-layouts \
  -p 'test_*.py' -v
```
