source "https://rubygems.org"

# GitHub Pages builds this site with its own pinned gem set (Pages build_type is
# "legacy", i.e. the built-in builder rather than Actions). Depending on the
# github-pages meta-gem keeps local builds identical to production, and pins us
# to the plugins Pages actually allows. It already provides jekyll-seo-tag,
# jekyll-sitemap, jekyll-feed, jekyll-redirect-from and jemoji, so those are not
# listed separately here — doing so only invites version conflicts.
gem "github-pages", group: :jekyll_plugins

gem "tzinfo-data"
gem "webrick", "~> 1.8" # removed from stdlib in Ruby 3.0; needed by `jekyll serve`
