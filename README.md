# dbutil
Python powered command line utility to use Danbooru more effectively.

### Disclaimer
This software is not an official product of Danbooru. See [LICENSE](LICENSE) for software accountability.

# Purpose
Many people use image aggregation sites like [Danbooru](https://danbooru.donmai.us) because they love browsing pictures and discovering images they love! On your first use, you browse page after page to like images and download favorites!

But then you leave, some time passes, and when you get back you see a new batch of images has been posted and you get to repeat this discovery all over again! The problem starts when you start to wonder, "Am I going to be able to search all the way back until where I started last time? And if I can't what posts am I missing?"

`dbutil` is a resource that uses the built in tools of Danbooru's [search tags](https://danbooru.donmai.us/wiki_pages/help%3Acheatsheet) to organize your browsing experience in a way that allows you to continue where you left off. 

# Intended Audience
This tool is intended for users of Danbooru with accounts, as you will be expected to use provide your username and [API Key](https://danbooru.donmai.us/wiki_pages/help:api). 

Although this software can be used by users with a [User Level](https://danbooru.donmai.us/wiki_pages/help%3Ausers) of "Member", because site behavior is controlled by search tags, this software is better utilized by members with a user level of "Gold" or higher. 

# Methodology
## Subsetting
Posts on Danbooru can be thought of in their simplest terms as a post ID, an integer value that represents the order in which a post was posted to the site. Each new post has an ID larger than those posted before, which also means that older posts have a smaller ID than younger posts. 

Danbooru can be thought of as a set of post IDs, $D={1,2,...,n}$ where $n$ is the post ID of the most recent post. As you add posts to your favorites, your favorites becomes a subset of all the posts on Danbooru, $F \subset D$. Because the favorites subset has post IDs contained within, we can determine a breadth of that subset range by finding the minimum value of that subset and the maximum value of that subset. 

With these $min$ and $max$ values, we can then tell Danbooru to use serve us a search set of posts, $S$. Based on our definition, we can tell danbooru to only provide us with images that were posted before, after, or within the bounds of our subset. 
- Before: $s\in S$ and $s < f \forall f \in F$
- After: $s\in S$ and $s > f \forall f \in F$
- Within: $s\in S$ and $F_(min) <= s <= F_(max)$

Subsetting only requires one search term.

### Subset Types
`dbutil` uses two subset types, and can discover the bounds of each. 
- Favorites
- Favgroups

## Directionality
We can use the `order` special search tag to tell Danbooru to present our search with either the youngest post being first ("order:id_desc" | ""), or the oldest post being first ("order:id"). 

## Finding the bounds of subsets
This software uses HTTP to communicate with the Danbooru API in order to learn the bounds of a given subset.
- Before requires 1 HTTP Request
- After requires 1 HTTP Request
- Within required 2 HTTP Requests

# Setup
## Package Requirements
Install the packages provided in `requirements.txt` into a python virtual environment (recommended) or global environment.

## Minimum Required Config Modification
Modify the `config.yaml` file with your preferred text editor. At a minimum, it is required that you provide the config file with your danbooru username and API key. Refer to the links above to gather this information.

⚠️Do not ever git commit sensitive information like usernames and API keys⚠️

It is optional but recommended that you create your own branch before modifying the config file.

## Optional Configuration Modifications
### web_base
Determines the base website that you intend to use. `dbutil` was designed and tested to work on Danbooru only! However the booru framework is used across multiple sites, so feel free to use `dbutil` on sites like Safebooru at your own risk.

### browser
Which Web Browser, if not the default, `dbutil` should use to launch the website. 

### page_launch_type
Tells `dbutil` how to launch the new web page, whether that be in a new browser window, or in a new tab.

## Saved Searches
Saved Searches in this case are not the same as the [Saved Searches](https://danbooru.donmai.us/saved_searches) on Danbooru. In this case a saved search is a `dbutil` configuration that provides a shortcut to the multiple steps required to implement the process defined in [methodology](#methodology). It's possible to use the methodology provided without `dbutil`, but the software automates the repetitive tasks of implementing the methodology. 

A saved search is defined with the following structure.
```yaml
example: # This is the name of your search that you will use when calling dbutil
  description: "Feel free to describe your search" # (Optional) A helpful reminder to you what this search does.
  # range_type describes a range that will be specified for the search.   
    # - none: No range is specified, the entirety of the site will be used.
    # - after: The search will only display posts posted after the youngest post in the subset
    # - before: The search will only display posts posted before the oldest post in the subset
    # - within: The search will only display posts posted between the oldest and youngest posts of the subset
  range_type: "after" # (Required)
  subset_type: "favgroup" # or "favorites" if the subset is the favorites list for your account. Required if range_type is not "none".
  favgroup_id: 1234 # Required if subset_type is "favgroup"
  saved_terms: "term_1 term_2" # (Optional) Additional terms that will always be added to this search
  direction: youngest_first # (Optional) youngest_first | oldest_first. Defaults to youngest first.
  # Suppose favgroup:1234 contains the posts {5, 6, 10, 8}.
  # When ran, this example will launch danbooru with the following search terms;
  # id:>10 term_1 term_2
```
You can add your own saved searches, E.G. for favorite groups, buy adding a saved search to the config file. 

# Pre-Defined Saved Searches
## launch
Launches the front page of Danbooru without typing it into your web browser! No subsetting is required.

## browse_new
`browse_new` is the primary motivation for making this utility! It looks at the most recent post that you've added to your favorites and launches danbooru with the order of `oldest first` so you can pick back up right where you left off! You can start right on page 1 and continue to add posts to your favorites with no breaks in the post ordering! You can stop at any time, and when you want to continue, you can run `browse_new` again and you'll be right where you stopped. When there are no more pages left in the search, that means that you're caught up to the present.

## browse_old
Finds the oldest post in your favorites list and browses after it. This allows you to keep going backward in time towards the first post to collect pictures you enjoy.

Includes the saved term of `-status:banned` to remove posts that have been taken down from the site from the search. These banned posts are typically disruptive to the browsing experience, to in many cases it's better to remove them if you can spare a search term. 

## safe_search
`safe_search` allows you to browse the site with some guardrails. Because the minimum and maximum of the subset are so important when defining the bounds of the subset, safe_search allows you to add to your subset without destroying the accuracy of the min and max of that subset. This is best used by [providing your own search tags](#how-to-run) as parameters!

# How to run
```cmd
python dbutil.py saved_search [search_tag_1] [search_tag_2]...
```
- `python` Your preferred python interpreter
- `dbutil.py` The main python script 
- `saved_search` Which saved search you want dbutil to launch. This saved search must be defined in `config.yaml`. One saved search must be required per execution.
- `search_tag_#` (Optional). You can optionally add your own search tags to further refine the search scope of what you're looking for from your saved search. If the `saved_search` already has `saved_terms` included in them, then these additional search terms will be added in addition to those `saved_terms`

# Additional Recommendations
## Add to your subset while you browse!
If you do not add to the subset while you're browsing, then when dbutil is run the next time, you will start off in the same place you did before. Each subset should be an ever expanding subset of posts that deserve to be included, or do not. Adding to your subset while you browse will allow `dbutil` to keep track of that progress for you.

You can use the tag_script mode to add posts to favorite groups as you browse, or you can use the favorite mode to add posts to your favorites list while you browse.

## Be careful of your maxims!
`dbutil` relies on the assumption that the youngest and oldest post of a subset really deserve to be there. 

Suppose you find a really old post that you want to save, you can add that post to a favorite group instead of your favorites if you want to maintain the integrity of your favorites list. 

## Use Blacklists rather than search tags
If you frequently run across posts with tags that you want to avoid, you don't have to waste search terms to hide them. Use the Blacklisted Tags field in [Settings](https://danbooru.donmai.us/settings) to hide posts that you do not want to see, and makes browsing much easier. 

# Future Improvements
Here is a list of tasks that could be done to improve `dbutil`

## Defined tasks
- [ ] Have `dbutil` parse config and saved searches as class data structures for added code readability
- [ ] Add fault tolerance for empty subsets
- [ ] Define test cases using https://testbooru.donmai.us to automate code validation
- - [ ] Launch
- - [ ] Saved Search with After
- - [ ] Saved Search with Before
- - [ ] Saved Search with Within
- - [ ] Saved Search with `saved_terms` defined
- - [ ] Saved Search with `direction` defined
- - [ ] Saved Search with search tag parameters passed to `dbutil`
- - [ ] Launch with new_window
- - [ ] Launch with new_tab

## Undefined tasks
- [ ] Improved maintainability
- [ ] Restructure as python application
- [ ] Certify for use on other booru websites
- [ ] More predefined saved searches