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

app = webapp2.WSGIApplication([('/?', handlers.MainPage),
							('/food/createUser.json', handlers.CreateUserJSON),
							('/food/test', handlers.AnotherPage),
							('/food/ratings', handlers.ObtainRatingsJSON),
							('/food/vote', handlers.VotePage),
							('/food/comment', handlers.VoteCommentPage)], 
								debug=True)



