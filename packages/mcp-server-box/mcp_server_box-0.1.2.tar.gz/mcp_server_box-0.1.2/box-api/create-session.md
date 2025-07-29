- [Sign up](https://account.box.com/signup/n/developer#ty9l3)

- [Box Platform](https://developer.box.com/platform/)
- [Box Sign](https://developer.box.com/sign/)
- [Box UI Elements](https://developer.box.com/box-ui-elements/)
- [Box AI Developer Zone](https://developer.box.com/ai-dev-zone/)

- [Developer Guides](https://developer.box.com/guides/)
- [API Reference](https://developer.box.com/reference/)

- [Sample Code Catalog](https://developer.box.com/sample-code/)
- [SDKs & Tools](https://developer.box.com/sdks-and-tools/)
- [Developer Changelog](https://developer.box.com/changelog/)
- [Box Developer Blog](https://medium.com/box-developer-blog)

- [Box Developer Community](https://community.box.com/)
- [Support](https://developer.box.com/support/)
- [Events](https://community.box.com/events?tab=upcoming)

- United States (English)
- 日本 (日本語)

[![Box Developer Documentation](<Base64-Image-Removed>)](https://developer.box.com/)

[Log in](https://account.box.com/login?redirect_url=%2Fdevelopers%2Fconsole "Log in")

GuidesEndpointsResourcesParams

# Chunked Uploads

[Guides](https://developer.box.com/guides/) [Uploads](https://developer.box.com/guides/uploads/) **Chunked Uploads**

[Edit this page](https://github.com/box/developer.box.com/blob/main/content/guides/uploads/chunked/index.md)

# Chunked Uploads

The Chunked Upload API provides a way to reliably upload large files to Box by
chunking them into a sequence of parts that can be uploaded individually.

By using this API the application uploads a file in part, allowing it to recover
from a failed request more reliably. It means an application only needs to
retry the upload of a single part instead of the entire file.

An additional benefit of chunked uploads is that parts can be uploaded
in parallel, allowing for a potential performance improvement.

## [Overview](https://developer.box.com/guides/uploads/chunked/\#overview)

Chunked uploads require a sequence of API calls to be made.

1. **[Create an upload session](https://developer.box.com/guides/uploads/chunked/create-session/)**: The application creates an upload session for a new file or new version of a file. The session defines the (new) name of the file, its size, and the parent folder.
2. **[Upload parts](https://developer.box.com/guides/uploads/chunked/upload-part/)**: The application uploads the separate parts of the file as chunks.
3. **[Commit session](https://developer.box.com/guides/uploads/chunked/commit-session/)**: The application commits the session, at which moment the integrity of the file is checked before it is placed in the location specified when the session was created.

Most of [the Box SDKs support chunked uploads](https://developer.box.com/guides/uploads/chunked/with-sdks/) out of the Box, removing
the complexity from the application code.

## [Restrictions](https://developer.box.com/guides/uploads/chunked/\#restrictions)

The Chunked Upload API is intended for large files with a minimum size of 20MB.
The API does not support uploads of files with a size smaller than this.

This API does not support re-uploading or overwriting of parts in a session.
Once a part has been uploaded, it is immutable.

The lifetime of an upload session is 7 days. During this time, the client can
upload parts at their own pace.

To avoid wasting resources, and avoid potential data corruption, client should
make sure that the underlying file has not been changed on disk since beginning
the upload.

[iframe](https://segment-box.com/?key=9mEaWAAXfspF6epYVozDiTF43jJErnJl)