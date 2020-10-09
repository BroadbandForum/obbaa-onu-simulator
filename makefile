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

# default target
html:

# distribution targets
dist:
	python3 setup.py sdist bdist_wheel

# XXX seem to need to distclean before doing pip install .
distclean: clean
	$(RM) -rf build dist $(wildcard *.egg-info)

# docker targets
DOCKER-ORG = broadbandforum
DOCKER-NAME = obbaa-onu-simulator
DOCKER-TAG = latest
DOCKER-IMAGE = $(DOCKER-ORG)/$(DOCKER-NAME):$(DOCKER-TAG)
DOCKER-CMD = bash

DOCKER-BUILDOPTS =
ifneq "$(FROM)" ""
  DOCKER-BUILDOPTS += --build-arg FROM=$(FROM)
endif
ifneq "$(NOCACHE)" ""
  DOCKER-BUILDOPTS += --no-cache
endif

# https://superuser.com/questions/1301499/
#	  running-wireshark-inside-a-centos-docker-container
DOCKER-RUNOPTS = -p 12345:12345/udp \
		 --cap-add=NET_RAW --cap-add=NET_ADMIN

docker-build:
	docker image build $(DOCKER-BUILDOPTS) --tag=$(DOCKER-IMAGE) .

docker-push: docker-build
	docker image push $(DOCKER-IMAGE)

docker-pull:
	docker image pull $(DOCKER-IMAGE)

docker-run:
	docker container run -it --name $(DOCKER-NAME) --rm $(DOCKER-RUNOPTS) $(DOCKER-IMAGE) $(DOCKER-CMD)

docker-exec:
	docker container exec -it $(DOCKER-NAME) $(DOCKER-CMD)

# adding the license
# XXX assumes that the BBF add-license.py utility is in PATH
# XXX should exclude some files?
ADD-LICENSE = add-license.py --license=LICENSE.declaration --project='' \
	--exclude docs/ --exclude share/ --loglevel=1 .

add-license:
	$(ADD-LICENSE)

remove-license:
	$(ADD-LICENSE) --remove

# sphinx-build handles remaining targets; make help to get a list
%:
	@sphinx-build -M $@ . docs -T
