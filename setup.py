# Copyright 2020 Broadband Forum
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

import setuptools

# XXX the link in this file is to a local file; how best to include the
#     sphinx documentation?
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name="obbaa-onusim", version="0.0.1",
                 author="William Lupton",
                 author_email="wlupton@broadband-forum.org",
                 description="ONU simulator and test client",
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url="https://github.com/BroadbandForum/obbaa-polt-simulator"
                     ".git", packages=setuptools.find_packages(),
                 scripts=["bin/onusim.py", "bin/onucli.py"],
                 classifiers=["Programming Language :: Python :: 3",
                              "License :: OSI Approved :: BSD License",
                              "Operating System :: OS Independent", ],
                 install_requires=[], python_requires='>=3.6', )
