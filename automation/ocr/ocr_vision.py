import os
import sys
import io
import pickle
from google.cloud import vision

fileName = ""

def detect_text(path):
  """Detects text in the file."""
  client = vision.ImageAnnotatorClient()

  with io.open(path, 'rb') as image_file:
    content = image_file.read()

  image = vision.Image(content=content)

  response = client.document_text_detection(image=image)
  texts = response.text_annotations
  print(texts)
  with io.open('poly.txt', 'w') as boundsFile:
    print(texts, file = boundsFile)
  boundsFile.close()

# Save output

  for text in texts:
    vertices = (['{},{}'.format(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices])
    print('{}'.format(text.description), end ="|")
    print('bounds|{}'.format('|'.join(vertices)))

  if response.error.message:
    raise Exception(
      '{}\nFor more info on error messages, check: '
      'https://cloud.google.com/apis/design/errors'.format(
      response.error.message))


def main():
  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "../../../visionapi.json"
  path = fileName

# Do OCR
  detect_text(path)

if __name__ == "__main__":
  fileName = sys.argv[1]
  main()
