# Plugin for Superdesk Live Blog embed
[![Build Status](https://travis-ci.org/liveblog/plugin-liveblog-embed-server.png?branch=master)](https://travis-ci.org/liveblog/plugin-liveblog-embed-server)
[![Coverage Status](https://coveralls.io/repos/liveblog/plugin-liveblog-embed-server/badge.png?branch=master)](https://coveralls.io/r/liveblog/plugin-liveblog-embed-server?branch=master)

This plugin for Sourcefabric’s Superdesk, first released as part of Live Blog 2.0 beta,  provides a solution for ensuring that blog content is indexable by search engines. A static HTML version of each blog is now generated on the server. As a publisher, you can set your CMS to request this HTML and insert it into an article page before that page is delivered to the browser. When search engine crawlers visit the page, they will see the latest posts from the embedded blog and index them. New posts are automatically added to the page via Javascript.

*License*: [AGPLv3](http://www.gnu.org/licenses/agpl-3.0.txt)

*Copyright*: [Sourcefabric z.ú.](http://www.sourcefabric.org)

## Setup

You will need [node.js](http://nodejs.org/) installed.

Once this is done, run the following commands from the root directory to install the rest of the dependencies:

```
npm install -g grunt-cli # install grunt
npm install -g bower # install bower
npm install # install node dependencies
bower install # install bower components
```

After that, you can start the local dev server on port `9000` running:

```
grunt server
```

## Documentation

Documentation can be generated in two ways:

a) With [Docco](http://jashkenas.github.io/docco/), the most used documentation generator.

Docco doesn't provide an index.html file for docs folder nor a structure for the content.

```
grunt docco:scripts # for source files
grunt docco:test # for test files
```

b) With [Docco Husky](https://github.com/mbrevoort/docco-husky), which extends Docco providing an index.html with stats.

Docco Husky is not being maintained. Last commit was done two years ago.

plugin-liveblog-embed-server is running a fork from `nistormihai` repo, kept up to date by the owner of the repo.

```
grunt docco-husky:scripts # for source files
grunt docco-husky:test # for test files
```

## Info for contributors

### Commit messages

Every commit has to have a meaningful commit message in the form:

```
[JIRA ref] [JIRA Title] or [Title]
<empty line>
[Description]
```

Where [JIRA ref](https://confluence.atlassian.com/display/FISHEYE/Using+smart+commits) is the Issue code eg. ```LB-13```.

For trivial changes you can ommit JIRA ref or Description or both eg. ```Add travis.yml files```

### Pull requests
Every pull request has to have a meaningful message and if not specified in the commits, a good description of what has been done.


### CI

You can test your code before sending a PR via: ```./travis_build.sh```
