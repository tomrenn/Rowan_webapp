#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

# setup template directory before importing all handlers
root_dir = os.path.dirname(__file__)
template_dir = os.path.join(root_dir, 'templates')

# this import is lower because template_dir must be predefined for handlers/base.py
import handlers.all as handlers
import handlers.front_end as front_end

app = webapp2.WSGIApplication([('/?', front_end.SplashPage),
							('/map/?', handlers.GoogleMap),
							('/food/createUser.json', handlers.CreateUserJSON),
							('/food/ratings', handlers.ObtainRatingsJSON),
							('/food/vote', handlers.VotePage),
							('/food/?', front_end.MainPage),
							('/food/webVote/?', front_end.VotePage),
							('/food/webComment/?', front_end.CommentPage),
							('/food/comment', handlers.VoteCommentPage)], 
								debug=True)



