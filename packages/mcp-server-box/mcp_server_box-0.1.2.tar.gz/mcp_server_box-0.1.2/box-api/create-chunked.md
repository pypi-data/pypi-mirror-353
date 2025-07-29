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

# Create Upload Session

[Guides](https://developer.box.com/guides/) [Uploads](https://developer.box.com/guides/uploads/) [Chunked Uploads](https://developer.box.com/guides/uploads/chunked/) **Create Upload Session**

[Edit this page](https://github.com/box/developer.box.com/blob/main/content/guides/uploads/chunked/create-session.md)

# Create Upload Session

To create an upload session, call the
[`POST /files/upload_sessions`](https://developer.box.com/reference/post-files-upload-sessions/) API with the desired `file_name`
and `folder_id` to put the file in, as well as the `file_size` of the file to be
uploaded.

To create a session for a new version of an existing file, call the
[`POST /files/:id/upload_sessions`](https://developer.box.com/reference/post-files-id-upload-sessions/) API instead. In this
case, the `file_name` and `folder_id` are only required when renaming or moving
the file in the process.

## [Pre-flight Check](https://developer.box.com/guides/uploads/chunked/create-session/\#pre-flight-check)

Creating an upload session also performs a [preflight check](https://developer.box.com/guides/uploads/check/), making it
unnecessary to do so separately when working with chunked uploads.

## [Response](https://developer.box.com/guides/uploads/chunked/create-session/\#response)

When a session is created successfully the response includes an [Upload\\
Session](https://developer.box.com/reference/resources/upload-session/) that includes a session ID, the number of parts, the
part sizes, as well as links to the relevant next API endpoints to use.

```json
{
  "id": "F971964745A5CD0C001BBE4E58196BFD",
  "type": "upload_session",
  "session_expires_at": "2012-12-12T10:53:43-08:00",
  "part_size": 1024,
  "total_parts": 1000,
  "num_parts_processed": 455,
  "session_endpoints": {
    "upload_part": "https://upload.box.com/api/2.0/files/upload_sessions/F971964745A5CD0C001BBE4E58196BFD",
    "commit": "https://upload.box.com/api/2.0/files/upload_sessions/F971964745A5CD0C001BBE4E58196BFD/commit",
    "abort": "https://upload.box.com/api/2.0/files/upload_sessions/F971964745A5CD0C001BBE4E58196BFD",
    "list_parts": "https://upload.box.com/api/2.0/files/upload_sessions/F971964745A5CD0C001BBE4E58196BFD/parts",
    "status": "https://upload.box.com/api/2.0/files/upload_sessions/F971964745A5CD0C001BBE4E58196BFD",
    "log_event": "https://upload.box.com/api/2.0/files/upload_sessions/F971964745A5CD0C001BBE4E58196BFD/log"
  }
}

```

The upload session defines the size of the parts to use when uploading the
individual parts.

# Related APIs

- [postCreate upload session](https://developer.box.com/reference/post-files-upload-sessions/)
- [postCreate upload session for existing file](https://developer.box.com/reference/post-files-id-upload-sessions/)

# Related Guides

- [GuideUpload Part](https://developer.box.com/guides/uploads/chunked/upload-part/)
- [GuideCommit Upload Session](https://developer.box.com/guides/uploads/chunked/commit-session/)

[iframe](https://segment-box.com/?key=9mEaWAAXfspF6epYVozDiTF43jJErnJl)[iframe](https://box.demdex.net/dest5.html?d_nsid=0#https%3A%2F%2Fdeveloper.box.com)