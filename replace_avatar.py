from cruds.assets import wasabi, S3_BUCKET, S3_DIR
from db import get_db, models
import re
import urllib

MIME_TYPE_DICT = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "bmp": "image/bmp",
    "gif": "image/gif",
    "mp4": "video/mp4",
    "mov": "video/quicktime",
    "avi": "video/x-msvideo",
    "flv": "video/x-flv",
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "m4a": "audio/aac",
    "zip": "application/zip",
    "gltf": "model/gltf+json",
    "default": "application/octet-stream",
}

session = next(get_db())

users: list[models.User] = session.query(models.User).all()

for user in users:
    print(user.name)
    print(user.avatar_url)
    if re.fullmatch(
        f"https://s3.ap-northeast-2.wasabisys.com/{S3_BUCKET}/{S3_DIR}/avatar/.+/origin.(png|jpg|jpeg|bmp|gif)",
        user.avatar_url,
    ):
        continue
    extension = user.avatar_url[user.avatar_url.rfind(".") + 1 :]
    try:
        req = urllib.request.Request(user.avatar_url)
        req.add_header("User-Agent", "Mozilla/5.0")
        file = urllib.request.urlopen(req)
        avatar_data = file.read()
    except urllib.error.URLError as e:
        print(e)
    wasabi.put_object(
        Body=avatar_data,
        Bucket=S3_BUCKET,
        Key=f"{S3_DIR}/avatar/{user.id}/origin.{extension}",
        ContentType=MIME_TYPE_DICT.get(extension, MIME_TYPE_DICT["default"]),
    )
    new_url = f"https://s3.ap-northeast-2.wasabisys.com/{S3_BUCKET}/{S3_DIR}/avatar/{user_id}/origin.{extension}"
    user.avatar_url = new_url

session.commit()
