# Copyright (c) 2020 Kaamiki Development Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author(s):
#     xames3 <44119552+xames3@users.noreply.github.com>

"""Default Kaamiki settings."""

# The below attribute shall never be changed, EVER!
TRIBUTE = 'Charlotte'

# This is the name of the concept and the framework. The name is
# purposely defined here so that it propagates in places where the
# title is expected.
MARK_ONE = 'Kaamiki'

# The framework adheres to Semantic Versioning Specification (SemVer)
# starting with version 0.0.1.
# You can read about it here: https://semver.org/spec/v2.0.0.html
# The version should be timely updated as progress is made.
FRAMEWORK_VERSION = '0.0.2'

# Author details. Since the framework is built with open source in
# mind, it is better to put all the authors, co-authors and
# contributors under the same umbrella.
AUTHOR = 'Kaamiki Development Team'
AUTHOR_EMAIL = 'xames3.kaamiki@gmail.com'

# Maintainer details, count of the below folks should probably
# increase in future, ** fingers cross **
MAINTAINER = 'xames3'
MAINTAINER_EMAIL = AUTHOR_EMAIL

# This is where all the entire source code, documentation, updates and
# bug reports will be hosted.
FRAMEWORK_URL = 'https://github.com/kaamiki/kaamiki'

# Open source software license used to publish the framework.
# Please note that the commented out header license should be involved
# in each and every valid module as it packs the terms and copyrights.
OSS_LICENSE = 'Apache Software License 2.0'

# One liner description of the framework. The description is bound
# to change as the progress is made.
SHORT_DESCRIPTION = ('Kaamiki is a simple cross-platform automation '
                     'framework for data science and machine learning tasks.')

# Flag which raises warning if the installed version of the framework
# is either outdated or a nightly (development) build.
# 0 = Fresh install or Update to the existing build.
# 1 = Checked build
# 2 = Beta (nightly build)
INSTALLATION_STATUS = 0

# Default time zone to be used if the choosing local time zone is not
# an available option.
DEFAULT_TZONE = 'UTC'

# If set to True, local time zone for the user will be used. This flag
# assumes that all the date time related events are handled in UTC by
# default.
USE_LOCAL_TZONE = False

# Default encoding standard to use for all StringIO operations.
DEFAULT_ENCODING = 'utf-8'

# Default seperator for strings and pathnames.
DEFAULT_SEPERATOR = '_'

# Default path for all framework related activities like logging, data
# acquisition and caching. This directory can be overridden by the user
# if needed.
# NOTE(xames3): The implementation of overriding DEFAULT_BASE_DIR over
#               user preference needs some serious thought.
DEFAULT_BASE_DIR = MARK_ONE.lower()
