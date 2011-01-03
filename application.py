from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app                                         
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api.images import Image,NotImageError
import urllib
import logging

class Blob(db.Model):
  blob_key = db.StringProperty()
  width = db.IntegerProperty()
  height = db.IntegerProperty()
  content_type = db.StringProperty()
  is_image = db.BooleanProperty()

# todo: add security so not just anyone can upload here
class CreateUploadTarget(webapp.RequestHandler):
  def get(self):
    redirect_url = self.request.get("uploadHandler")
    uuid = self.request.get("uuid")
    logging.debug("Redirect after Upload URL: %s" % redirect_url)
    local_path = "%s/handleUpload" % self.request.url.replace(self.request.path, "").replace("?" + self.request.query_string, "")
    full_path = "%s?redirect=%s&uuid=%s" % (local_path, redirect_url, uuid)
    logging.debug("Upload Handler Callback: %s" % full_path)
    upload_url = blobstore.create_upload_url(full_path)
    self.response.content_type = "text/plain"
    self.response.out.write(upload_url)

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    redirect = self.request.get("redirect")
    uuid = self.request.get("uuid")
    upload_files = self.get_uploads('file')
    blob_info = upload_files[0]

    #redirect to callback with blob key and uuid
    redirect_url = "%s?blobKey=%s&uuid=%s" % (redirect, blob_info.key(), uuid)
    logging.debug("Redirect Url: %s" % redirect_url)

    self.store_info(blob_info)

    self.redirect(redirect_url)

  def store_info(self, blob_info):
    b = Blob()
    img = Image(None, blob_info)

    b.blob_key = str(blob_info.key())
    b.content_type = blob_info.content_type
    b.is_image = True

    try:
      b.width = img.width
      b.height = img.height
    except NotImageError:
      b.is_image = False

    b.put()

class ServeBlobHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)

application = webapp.WSGIApplication([
      ('/createUploadTarget', CreateUploadTarget),
      ('/handleUpload', UploadHandler),
      ('/serve/([^/]+)?', ServeBlobHandler)
    ], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
