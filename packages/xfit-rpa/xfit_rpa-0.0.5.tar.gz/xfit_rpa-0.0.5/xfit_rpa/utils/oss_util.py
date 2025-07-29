import oss2


class OssUtil:
    def __init__(self, access_key_id, access_key_secret, endpoint, bucket_name, **kwargs):
        self._auth = oss2.Auth(access_key_id, access_key_secret)
        self._bucket = oss2.Bucket(self._auth, endpoint, bucket_name)
        self._upload_dir = kwargs.get('upload_dir', None)
        self._kwargs = kwargs

    def get_bucket(self):
        return self._bucket

    def upload_object(self, object_name, file_path):
        if self._upload_dir and object_name.find(self._upload_dir) == -1:
            object_name = self._upload_dir + object_name
        result = self._bucket.put_object_from_file(object_name, file_path)
        return result

    def move_object(self, src_object_name, dest_object_name):
        result = self._copy_object(src_object_name, dest_object_name)
        if result.status == 200:
            result = self._delete_object(src_object_name)
        return result

    def _copy_object(self, src_object_name, dest_object_name):
        result = self._bucket.copy_object(self._bucket.bucket_name, src_object_name, dest_object_name)
        return result

    def _delete_object(self, object_name):
        result = self._bucket.delete_object(object_name)
        return result

    def list_objects(self, prefix, **kwargs):
        result = self._bucket.list_objects(prefix=prefix, **kwargs)
        return result
