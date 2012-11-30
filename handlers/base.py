import jinja2
import webapp2

from main import template_dir

# Initalize the jinja2 environment
jinja_environment = jinja2.Environment(autoescape=False,
 loader=jinja2.FileSystemLoader(template_dir))

# Base Handler with tailored functions
class AppHandler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str(self, template, **params):
    t = jinja_environment.get_template(template)
    return t.render(params)

  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))