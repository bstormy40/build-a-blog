import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    blogpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class NewPostPage(Handler):
    def render_blog(self, title="", blogpost = "", error=""):
        self.render("newpost.html", title=title, blogpost=blogpost, error=error,)

    def get(self):
        self.render_blog()

    def post(self):
        title = self.request.get("title")
        blogpost = self.request.get("blogpost")

        if title and blogpost:
            bp = BlogPost(title = title, blogpost = blogpost)
            bp.put()
            post_id = (bp.key().id())

            self.redirect("/blog/" + str(post_id))
        else:
            error = "We need both a title and some words!"
            self.render_blog(title, blogpost, error)

class BlogPage(Handler):
    def render_blog(self, title="", blogpost = ""):
        blogposts = db.GqlQuery("SELECT * FROM BlogPost "
                            "ORDER BY created DESC LIMIT 5")
        self.render("blog.html", title=title, blogpost=blogpost, blogposts = blogposts)

    def get(self):
        self.render_blog()

class ViewPost(Handler):
    def get(self, id):
        data = BlogPost.get_by_id (int(id))

        if not data:
            return self.error(404)

        self.render("permalink.html", data = data)

app = webapp2.WSGIApplication([
    ('/blog', BlogPage),
    ('/newpost', NewPostPage),
    (webapp2.Route('/blog/<id:\d+>', ViewPost))
],
    debug=True)
