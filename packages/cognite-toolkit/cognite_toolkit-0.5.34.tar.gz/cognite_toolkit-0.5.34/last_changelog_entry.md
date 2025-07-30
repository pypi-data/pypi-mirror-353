## cdf 

### Improved

- The `cdf dump timeseries/assets` now has a standardized order for
columns.
- The `cdf dump timeseries/assets` now splits into multiple files if the
size is above 128MB.
- [performance] The `cdf dump timeseries/assets` no longer writes files
twice to ensure all columns are the same. Now, it looks up column
headers before starting the dump process.

## templates

No changes.