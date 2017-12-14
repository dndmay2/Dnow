# Dnow
Necessary for style sheets to work.
https://devcenter.heroku.com/articles/django-assets

(venv) [529] ~/dev/dnow/churchsite > heroku local web


  529  heroku local web
  530  heroku login
  531  heroku create
  532  git push heroku master

  Fixed a staticfiles error
  533  heroku config:set DISABLE_COLLECTSTATIC=0

  534  git push heroku master
  535  heroku logs
  536  pip freeze
