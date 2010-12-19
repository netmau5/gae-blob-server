from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import urllib
import logging

# todo: add security so not just anyone can upload here
class CreateUploadTarget(webapp.RequestHandler):
  def get(self):
    redirect_url = self.request.get("uploadHandler")
    logging.debug("Redirect after Upload URL: %s" % redirect_url)
    local_path = "%s/handleUpload" % self.request.url.replace(self.request.path, "").replace("?" + self.request.query_string, "")
    full_path = "%s?redirect=%s" % (local_path, redirect_url)
    logging.debug("Upload Handler Callback: %s" % full_path)
    upload_url = blobstore.create_upload_url(full_path)
    self.response.content_type = "text/plain"
    self.response.out.write(upload_url)

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    redirect = self.request.get("redirect")
    logging.info("Redirect URL: %s" % redirect)
    upload_files = self.get_uploads('file')
    blob_info = upload_files[0]
    #redirect to callback with blob key
    self.redirect("%s?blobKey=%s" % (redirect, blob_info.key()))

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
