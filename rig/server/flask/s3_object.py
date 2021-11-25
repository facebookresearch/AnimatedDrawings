import boto3
import botocore

class s3_object:

    global s3 
    global s3_client 
    s3 = boto3.resource('s3')
    s3_client = boto3.client('s3')
    
    def __init__(self, BUCKET):
      self.BUCKET = BUCKET

    def write_object(self, PREFIX, OBJECTNAME, DATA):
        s3_object = s3.Object(self.BUCKET,PREFIX+"/%s" % OBJECTNAME)
        s3_object.put(Body=DATA)
    
    def verify_object(self, PREFIX, OBJECTNAME):
        list_objects = s3_client.list_objects(Bucket=self.BUCKET, Prefix=PREFIX+"/", Delimiter='/')
        list_objects = [i['Key'] for i in list_objects['Contents']]       
        if PREFIX+"/%s" % OBJECTNAME  in list_objects:
            return True
        else:
            return False
    
    def get_object_bytes(self, PREFIX, OBJECTNAME):
        return s3.Object(self.BUCKET, PREFIX+"/%s" % OBJECTNAME).get()['Body'].read()
    
    def verify_directory(self, PREFIX):
        try:
            res = s3_client.list_objects_v2(
            Bucket = self.BUCKET,
            Prefix = PREFIX
        )
            if isinstance(res['Contents'], list) == True:
                return True
        except KeyError:
            return False

    def verify_sub_directory(self, PREFIX, SUBFOLDER):
        res = s3_client.list_objects_v2(
                Bucket = self.BUCKET,
                Prefix = PREFIX)
        folderlist = [i['Key'] for i in res['Contents']]
        if "%s/%s/" % (PREFIX, SUBFOLDER) in folderlist:
            return True
        else:
            return False
    
    def delete_directory(self, PREFIX):
        delete_prefix = s3.Bucket(self.BUCKET)
        delete_prefix.objects.filter(Prefix=PREFIX).delete()
    
    def create_subfolder(self, PREFIX, SUBFOLDER):
        s3_client.put_object(Bucket=self.BUCKET, Key='%s/%s/' % (PREFIX, SUBFOLDER))

if __name__ == "__main__":
    s3_object()
