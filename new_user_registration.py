import boto3
import json

def detect_faces(target_file, region):

    client=boto3.client('rekognition', region_name=region)

    imageTarget = open(target_file, 'rb')

    response = client.detect_faces(Image={'Bytes': imageTarget.read()}, 
    Attributes=['ALL'])

    print('Detected faces for ' + photo)
    for faceDetail in response['FaceDetails']:
        print('The detected face is between ' + str(faceDetail['AgeRange']['Low'])
              + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')

        print('Here are the other attributes:')
        print(json.dumps(faceDetail, indent=4, sort_keys=True))

        # Access predictions for individual face details and print them
        print("Gender: " + str(faceDetail['Gender']))
        print("Smile: " + str(faceDetail['Smile']))
        print("Eyeglasses: " + str(faceDetail['Eyeglasses']))
        print("Emotions: " + str(faceDetail['Emotions'][0]))

    return len(response['FaceDetails'])

photo = 'olivia_johnson_initial.jpeg'
region = 'us-east-1'
face_count=detect_faces(photo, region)
print("Faces detected: " + str(face_count))

if face_count == 1:
    print("Image suitable for use in collection.")
else:
    print("Please submit an image with only one face.")

# def compare_faces(bucket, sourceFile, targetFile, region):
#     client = boto3.client('rekognition', region_name=region)

#     imageTarget = open(targetFile, 'rb')

#     response = client.compare_faces(SimilarityThreshold=99,
#                                     SourceImage={'S3Object':{'Bucket':bucket,'Name':sourceFile}},
#                                     TargetImage={'Bytes': imageTarget.read()})

#     for faceMatch in response['FaceMatches']:
#         position = faceMatch['Face']['BoundingBox']
#         similarity = str(faceMatch['Similarity'])
#         print('The face at ' +
#               str(position['Left']) + ' ' +
#               str(position['Top']) +
#               ' matches with ' + similarity + '% confidence')

#     imageTarget.close()
#     return len(response['FaceMatches'])

# bucket = 'facial-recognition-solomon-berry'
# target_file = 'olivia_johnson_initial.jpeg'
# source_file = 'login_images/solomon_berry'
# /region = "us-east-1"
# face_matches = compare_faces(bucket, source_file, target_file, region)
# print("Face matches: " + str(face_matches))

# if str(face_matches) == "1":
#     print("Face match found.")
# else:
#     print("No face match found.")

collectionId = 'facial_recognition_login'
region = "us-east-1"
photo = 'olivia_johnson_initial.jpeg'
threshold = 99
maxFaces = 1
client = boto3.client('rekognition', region_name=region)

# input image should be local file here, not s3 file
with open(photo, 'rb') as image:
    response = client.search_faces_by_image(CollectionId=collectionId,
    Image={'Bytes': image.read()},
    FaceMatchThreshold=threshold, MaxFaces=maxFaces)

faceMatches = response['FaceMatches']
print(faceMatches)

for match in faceMatches:
    print('FaceId:' + match['Face']['FaceId'])
    print('ImageId:' + match['Face']['ImageId'])
    print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
    print('Confidence: ' + str(match['Face']['Confidence']))

def add_faces_to_collection(target_file, photo, collection_id, region):
    client = boto3.client('rekognition', region_name=region)

    imageTarget = open(target_file, 'rb')

    response = client.index_faces(CollectionId=collection_id,
                                  Image={'Bytes': imageTarget.read()},
                                  ExternalImageId=photo,
                                  MaxFaces=1,
                                  QualityFilter="AUTO",
                                  DetectionAttributes=['ALL'])
    print(response)

    print('Results for ' + photo)
    print('Faces indexed:')
    for faceRecord in response['FaceRecords']:
        print('  Face ID: ' + faceRecord['Face']['FaceId'])
        print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))
        print('  Image ID: {}'.format(faceRecord['Face']['ImageId']))
        print('  External Image ID: {}'.format(faceRecord['Face']['ExternalImageId']))
        print('  Confidence: {}'.format(faceRecord['Face']['Confidence']))

    print('Faces not indexed:')
    for unindexedFace in response['UnindexedFaces']:
        print(' Location: {}'.format(unindexedFace['FaceDetail']['BoundingBox']))
        print(' Reasons:')
        for reason in unindexedFace['Reasons']:
            print('   ' + reason)
    return len(response['FaceRecords'])

image = 'olivia_johnson_initial.jpeg'
collection_id = 'facial_recognition_login'
photo_name = 'olivia_johnson'
region = "us-east-1"

indexed_faces_count = add_faces_to_collection(image, photo_name, collection_id, region)
print("Faces indexed count: " + str(indexed_faces_count))

import logging
from botocore.exceptions import ClientError

# store local file in S3 bucket
bucket = "facial-recognition-solomon-berry"
file_name = "olivia_johnson_initial.jpeg"
key_name = "olivia-johnson"
region = "us-east-1"
s3 = boto3.client('s3', region_name=region)
# Upload the file
try:
    response = s3.upload_file(file_name, bucket, key_name)
    print("File upload successful!")
except ClientError as e:
    logging.error(e)


from pprint import pprint
from decimal import Decimal

# Get URL of file
file_url = "https://s3.amazonaws.com/{}/{}".format(bucket, key_name)
print(file_url)

# upload face-id, face info, and image url
def AddDBEntry(file_name, file_url, face_id, image_id, confidence):
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table('facial_rekognition')
    response = table.put_item(
       Item={
            'ExternalImageID': file_name,
            'ImageURL': file_url,
            'FaceID': face_id,
            'ImageID': image_id, 
            'Confidence': json.loads(json.dumps(confidence), parse_float=Decimal)
       }
    )
    return response

# Mock values for face ID, image ID, and confidence - replace them with actual values from your collection results
dynamodb_resp = AddDBEntry(file_name, file_url, "89e62c66-60fd-4fc9-84b2-97563f938960",  
    "98ea4e2b-0d5f-3555-b4c8-0037284a31fe", 99.99951171875)
print("Database entry successful.")
pprint(dynamodb_resp, sort_dicts=False)

# Faces indexed:
#   Face ID: 89e62c66-60fd-4fc9-84b2-97563f938960
#   Location: {'Width': 0.5795125365257263, 'Height': 0.6852100491523743, 'Left': 0.23001201450824738, 'Top': 0.20693688094615936}
#   Image ID: 98ea4e2b-0d5f-3555-b4c8-0037284a31fe
#   External Image ID: solomon_berry
#   Confidence: 99.99951171875