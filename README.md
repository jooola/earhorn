# earhorn

Listen, monitor and archive your streams!

[![](https://mermaid.ink/svg/eyJjb2RlIjoic3RhdGVEaWFncmFtLXYyXG4gICAgc3RhdGUgXCJTdGFydCBldmVudCBoYW5kbGVyXCIgYXMgc3RhcnRfaGFuZGxlclxuICAgIFsqXSAtLT4gc3RhcnRfaGFuZGxlclxuXG4gICAgc3RhdGUgXCJDaGVjayByZW1vdGUgc3RyZWFtXCIgYXMgY2hlY2tfc3RyZWFtXG4gICAgc3RhcnRfaGFuZGxlciAtLT4gY2hlY2tfc3RyZWFtXG5cbiAgICBzdGF0ZSBpZl9zdHJlYW1fb2sgPDxjaG9pY2U-PlxuICAgIHN0YXRlIHN0YXJ0IDw8Zm9yaz4-XG4gICAgY2hlY2tfc3RyZWFtIC0tPiBpZl9zdHJlYW1fb2s6IElzIHRoZSBzdHJlYW0gb2sgP1xuXG4gICAgaWZfc3RyZWFtX29rIC0tPiBzdGFydDogWWVzXG4gICAgc3RhdGUgXCJTdGFydCBsaXN0ZW5lclwiIGFzIHN0YXJ0X2xpc3RlbmVyXG4gICAgc3RhdGUgXCJTdGFydCByZWNvcmRlclwiIGFzIHN0YXJ0X3JlY29yZGVyXG4gICAgc3RhcnQgLS0-IHN0YXJ0X2xpc3RlbmVyXG4gICAgc3RhcnQgLS0-IHN0YXJ0X3JlY29yZGVyXG5cbiAgICBzdGF0ZSBcIlNlbmQgZXJyb3IgdG8gZXZlbnQgaGFuZGxlclwiIGFzIHNlbmRfZXJyb3JcbiAgICBzdGF0ZSBcIldhaXQgZm9yIDUgc2Vjb25kc1wiIGFzIHdhaXRfc3RyZWFtX29rXG4gICAgaWZfc3RyZWFtX29rIC0tPiBzZW5kX2Vycm9yOiBOb1xuICAgIHNlbmRfZXJyb3IgLS0-IHdhaXRfc3RyZWFtX29rXG4gICAgd2FpdF9zdHJlYW1fb2sgLS0-IGNoZWNrX3N0cmVhbVxuXG4gICAgc3RhdGUgXCJSdW4gKHVudGlsIGV4aXQgb3IgZXJyb3IgcmFpc2VkKVwiIGFzIHJ1bm5pbmdcbiAgICBzdGFydF9saXN0ZW5lciAtLT4gcnVubmluZ1xuICAgIHN0YXJ0X3JlY29yZGVyIC0tPiBydW5uaW5nXG5cbiAgICBydW5uaW5nIC0tPiBjaGVja19zdHJlYW06IEVycm9yIHJhaXNlZFxuXG4gICAgcnVubmluZyAtLT4gWypdIiwibWVybWFpZCI6eyJ0aGVtZSI6ImRlZmF1bHQifSwidXBkYXRlRWRpdG9yIjpmYWxzZSwiYXV0b1N5bmMiOnRydWUsInVwZGF0ZURpYWdyYW0iOmZhbHNlfQ)](https://mermaid.live/edit#eyJjb2RlIjoic3RhdGVEaWFncmFtLXYyXG4gICAgc3RhdGUgXCJTdGFydCBldmVudCBoYW5kbGVyXCIgYXMgc3RhcnRfaGFuZGxlclxuICAgIFsqXSAtLT4gc3RhcnRfaGFuZGxlclxuXG4gICAgc3RhdGUgXCJDaGVjayByZW1vdGUgc3RyZWFtXCIgYXMgY2hlY2tfc3RyZWFtXG4gICAgc3RhcnRfaGFuZGxlciAtLT4gY2hlY2tfc3RyZWFtXG5cbiAgICBzdGF0ZSBpZl9zdHJlYW1fb2sgPDxjaG9pY2U-PlxuICAgIHN0YXRlIHN0YXJ0IDw8Zm9yaz4-XG4gICAgY2hlY2tfc3RyZWFtIC0tPiBpZl9zdHJlYW1fb2s6IElzIHRoZSBzdHJlYW0gb2sgP1xuXG4gICAgaWZfc3RyZWFtX29rIC0tPiBzdGFydDogWWVzXG4gICAgc3RhdGUgXCJTdGFydCBsaXN0ZW5lclwiIGFzIHN0YXJ0X2xpc3RlbmVyXG4gICAgc3RhdGUgXCJTdGFydCByZWNvcmRlclwiIGFzIHN0YXJ0X3JlY29yZGVyXG4gICAgc3RhcnQgLS0-IHN0YXJ0X2xpc3RlbmVyXG4gICAgc3RhcnQgLS0-IHN0YXJ0X3JlY29yZGVyXG5cbiAgICBzdGF0ZSBcIlNlbmQgZXJyb3IgdG8gZXZlbnQgaGFuZGxlclwiIGFzIHNlbmRfZXJyb3JcbiAgICBzdGF0ZSBcIldhaXQgZm9yIDUgc2Vjb25kc1wiIGFzIHdhaXRfc3RyZWFtX29rXG4gICAgaWZfc3RyZWFtX29rIC0tPiBzZW5kX2Vycm9yOiBOb1xuICAgIHNlbmRfZXJyb3IgLS0-IHdhaXRfc3RyZWFtX29rXG4gICAgd2FpdF9zdHJlYW1fb2sgLS0-IGNoZWNrX3N0cmVhbVxuXG4gICAgc3RhdGUgXCJSdW4gKHVudGlsIGV4aXQgb3IgZXJyb3IgcmFpc2VkKVwiIGFzIHJ1bm5pbmdcbiAgICBzdGFydF9saXN0ZW5lciAtLT4gcnVubmluZ1xuICAgIHN0YXJ0X3JlY29yZGVyIC0tPiBydW5uaW5nXG5cbiAgICBydW5uaW5nIC0tPiBjaGVja19zdHJlYW06IEVycm9yIHJhaXNlZFxuXG4gICAgcnVubmluZyAtLT4gWypdIiwibWVybWFpZCI6IntcbiAgXCJ0aGVtZVwiOiBcImRlZmF1bHRcIlxufSIsInVwZGF0ZUVkaXRvciI6ZmFsc2UsImF1dG9TeW5jIjp0cnVlLCJ1cGRhdGVEaWFncmFtIjpmYWxzZX0)

## Install

```sh
sudo apt install ffmpeg
pip install earhorn
```

```sh
earhorn --archive-path=/to/my/archive https://stream.example.org/live.ogg
```

### Docker

```sh
docker pull ghcr.io/jooola/earhorn
```

## Usage

```
Usage: earhorn [OPTIONS] URL

  URL of the stream.

Options:
  --hook PATH                       Hook to run to handle events.
  --archive-path PATH               Path to the archive directory.
  --archive-segment-size INTEGER    Archive segment size in seconds.  [default: 3600]
  --archive-segment-filename TEXT   Archive segment filename (without extension).  [default: archive-%Y%m%d_%H%M%S]
  --archive-segment-format TEXT     Archive segment format.  [default: ogg]
  --help                            Show this message and exit.

```

## Releases

To release a new version, first bump the version number in `pyproject.toml` by hand or by using:

```sh
# poetry version --help
poetry version <patch|minor|major>
```

Run the release target:

```sh
make release
```

Finally, push the release commit and tag to publish them to Pypi:

```sh
git push --follow-tags
```
