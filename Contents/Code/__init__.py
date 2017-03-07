from DumbTools import DumbKeyboard

ART = 'plexcasts_art.jpg'
ICON = 'plexcasts_icon.png'
ADD = 'plexcasts_add.png'
FIND = 'plexcasts_find.png'
MINUS = 'plexcasts_remove.png'
NEXT = 'plexcasts_next.png'
BACK = 'plexcasts_back.png'

####################################################################################################
def Start():
	Plugin.AddViewGroup("Podcasts", viewMode="InfoList")
	Plugin.AddViewGroup("PodcastEpisode", viewMode="InfoList")

	ObjectContainer.view_group = 'Podcasts'
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = 'PlexCasts'
	TrackObject.thumb = R(ICON)

	# Initialize Dict if it does not exist yet
	if not Dict['podcastlist']:
		Dict['podcastlist'] = []

#	Dict['podcastlist'] = []
#	Dict.save()

####################################################################################################     
@handler('/music/plexcasts', 'PlexCasts', thumb=ICON, art=ART)
def MainMenu():
	
	oc = ObjectContainer(view_group="Podcasts")

	oc.add(DirectoryObject(key=Callback(PodcastMenu), title="My Podcasts", thumb = R(ICON)))

	if Client.Product in DumbKeyboard.clients:
		DumbKeyboard('/music/plexcasts/find', oc, Search,
			dktitle = 'Find Podcast',
			dkthumb = R(FIND))
	else:
	    oc.add(InputDirectoryObject(key=Callback(Search), title="Find Podcast", thumb = R(FIND)))

	return oc

####################################################################################################     
@route('/music/plexcasts/podcasts')
def PodcastMenu():

	oc = ObjectContainer(view_group="Podcasts")
	oc.title1 = 'My Podcasts'


	for x in Dict['podcastlist']:

		try:
			oc.add(DirectoryObject(key=Callback(PodcastEpisodeMenu, title=x[0], feedurl=x[1], offset=0, showAdd="False"), title=x[0], summary=x[2], thumb = x[3]))
		except:
			pass

	return oc

####################################################################################################
@route('/music/plexcasts/podcast')
def PodcastEpisodeMenu(title, feedurl, offset, showAdd):

	oc = ObjectContainer(view_group="PodcastEpisode")
	try:
		feed = RSS.FeedFromURL(feedurl)

		if showAdd == "True":
			oc.title1 = 'Listen or add podcast'
			oc.add(DirectoryObject(key=Callback(AddPodcast, podcastURL=feedurl, podcastName=feed.channel.title, podcastSummary=feed.channel.description, podcastIcon=feed.channel.image.url), title="Add Podcast", thumb = R(ADD)))
		else:
			oc.title1 = title


		displayCount = int(Prefs["DisplayCount"])
		offset = int(offset)

		if Prefs["Sortord"]:
			mal = 1
		else:
			mal = -1

		for item in feed.entries[::mal][offset:offset+displayCount]:

			url = item.enclosures[0]['url']
			showtitle = item.title
			summary = String.StripTags(item.summary)
			if len( summary) == 0:
				summary = "- No episode details -"
			
			try:
				image = str(feed.channel.image.url)
				oc.add(CreateTrackObject(url=url, title=showtitle, thumb=image, summary=summary))
				oc.art=image
				oc.title1=feed.channel.title
			except:
				pass

		if (len(feed.entries)-offset) > displayCount:
			oc.add(DirectoryObject(key=Callback(PodcastEpisodeMenu, title=title, feedurl=feedurl, offset=offset+displayCount), title="Next", thumb = R(NEXT)))

	except Exception, e:
		Log ( 'Exception while reading feed')
		Log ( e)
		oc = ObjectContainer(header='Problem with prodcast', message='There was a problem viewing this Podcast, please try again or remove it.')
		oc.add(DirectoryObject(key=Callback(MainMenu), title="Back", thumb = R(BACK)))
		pass

	for x in Dict['podcastlist']:
		try:
			if x[1] == feedurl:
				oc.add(DirectoryObject(key=Callback(DelPodcast, feedObj=x), title="Remove Podcast", summary="Removes this Podcast from your list", thumb = R(MINUS)))
		except:
			pass

	return oc

####################################################################################################     
@route('/music/plexcasts/add')
def AddPodcast( podcastURL=None, podcastName=None, podcastSummary=None, podcastIcon=None):

	oc = ObjectContainer(no_cache=True)
	oc.title1 = 'Podcast added'

	if (podcastURL != None) and (podcastName != None) and (podcastSummary != None) and (podcastIcon != None):

		ugly = [podcastName, podcastURL, podcastSummary, podcastIcon]

		if ugly not in Dict['podcastlist']:
			Dict['podcastlist'].append(ugly)

		Dict['podcastlist'].sort(key=lambda x: x[0])
		Dict.Save()

	oc.add(DirectoryObject(key=Callback(MainMenu), title="Back", thumb = R(BACK)))

	return oc

####################################################################################################
@route('/music/plexcasts/delete')
def DelPodcast(feedObj):

	oc = ObjectContainer(no_cache=True)

	try:	
		Dict['podcastlist'].remove(feedObj)
		Dict.Save()
	except:
		pass

	oc.add(DirectoryObject(key=Callback(MainMenu), title="Back", thumb = R(BACK)))
	return oc

####################################################################################################
def CreateTrackObject(url, title, thumb, summary, include_container=False):

	if url.endswith('.mp3'):
		container = 'mp3'
		audio_codec = AudioCodec.MP3
	else:
		container = Container.MP4
		audio_codec = AudioCodec.AAC

	track_object = TrackObject(
		key = Callback(CreateTrackObject, url=url, title=title, thumb=thumb, summary=summary, include_container=True),
		rating_key = url,
		title = title,
		thumb=thumb,
		summary = summary,
		items = [
			MediaObject(
				parts = [
					PartObject(key=url)
				],
				container = container,
				audio_codec = audio_codec,
				audio_channels = 2
			)
		]
	)

	if include_container:
		return ObjectContainer(objects=[track_object])
	else:
		return track_object

####################################################################################################
@route('/music/plexcasts/find', 'Find Podcast', thumb=ICON, art=ART)
def Search(query):

	oc = ObjectContainer(no_cache=True)
	oc.title1 = 'Select podcast to add'
	neary = str(query.replace (" ", "+"))
	pod = JSON.ObjectFromURL("https://itunes.apple.com/search?term=%s&entity=podcast&limit=26" % neary)['results']

	for x in pod:
		oc.add(DirectoryObject(key=Callback(PodcastEpisodeMenu, title=[x][0]['collectionName'], feedurl=[x][0]['feedUrl'], offset=0, showAdd="True"), title=[x][0]['collectionName'], thumb=[x][0]['artworkUrl600']))

	return oc
