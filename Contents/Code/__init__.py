from DumbTools import DumbKeyboard

ART = 'plexcasts_art.jpg'
ICON = 'plexcasts_icon.png'
PLUS = 'plexcasts_find.png'
MINUS = 'plexcasts_remove.png'
NEXT = 'plexcast_next.png'
BACK = 'plexcasts_back.png'

####################################################################################################
def Start():

	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = 'PlexCasts'
	TrackObject.thumb = R(ICON)

	# Initialize Dict if it does not exist yet
	if not Dict['feed']:
		Dict['feed'] = []

####################################################################################################     
@handler('/music/plexcasts', 'PlexCasts', thumb=ICON, art=ART)
def MainMenu(nameofshow=None, urlofshow=None, artofshow=None):

	oc = ObjectContainer()

	if (nameofshow != None) and (urlofshow != None) and (artofshow != None):

		ugly = [nameofshow, urlofshow, artofshow]

		if ugly not in Dict['feed']:
			Dict['feed'].append(ugly)

		Dict['feed'].sort(key=lambda x: x[0])
		Dict.Save()

	for x in Dict['feed']:

		try:
			oc.add(DirectoryObject(key=Callback(SecondMenu, title=x[0], feedurl=x[1], offset=0), title=x[0], thumb = x[2]))
		except:
			pass

	if Client.Product in DumbKeyboard.clients:
		DumbKeyboard('/music/plexcasts/find', oc, Search,
			dktitle = 'Find Podcast',
			dkthumb = R(PLUS))
	else:
	    oc.add(InputDirectoryObject(key=Callback(Search), title="Find Podcast", thumb = R(PLUS)))

#	oc.add(DirectoryObject(key=Callback(DelMenu, title="Delete a Podcast"), title="Delete a Podcast", thumb = R(MINUS)))

	return oc

####################################################################################################
def DelMenu(feedObj):

	oc = ObjectContainer()

	try:	
		Dict['feed'].remove(feedObj)
		Dict.Save()
	except:
		pass

#	for x in Dict['feed']:

#		try:
#			oc.add(DirectoryObject(key=Callback(DelMenu, title=x), title=x[0], thumb = x[2]))
#		except:
#			pass

	oc.add(DirectoryObject(key=Callback(MainMenu), title="Back", thumb = R(BACK)))
	return oc

####################################################################################################
def SecondMenu(title, feedurl, offset):

	oc = ObjectContainer()
	try:
		feed = RSS.FeedFromURL(feedurl)

		if Prefs["Sortord"]:
			mal = 1
		else:
			mal = -1

		for item in feed.entries[::mal][offset:offset+26]:

			url = item.enclosures[0]['url']
			showtitle = item.title
			summary = String.StripTags(item.summary)

			try:
				image = str(feed.channel.image.url)
				oc.add(CreateTrackObject(url=url, title=showtitle, thumb=image, summary=summary))
				oc.art=image
				oc.title1=feed.channel.title
			except:
				pass

		oc.add(DirectoryObject(key=Callback(SecondMenu, title=title, feedurl=feedurl, offset=offset+26), title="Next", thumb = R(NEXT)))
	except Exception, e:
		Log ( 'Exception while reading feed')
		Log ( e)
		oc = ObjectContainer(header='Problem with prodcast', message='There was a problem viewing this Podcast, please try again or remove it.')
		oc.add(DirectoryObject(key=Callback(MainMenu), title="Back", thumb = R(BACK)))
		pass


	for x in Dict['feed']:
		try:
			if x[1] == feedurl:
				oc.add(DirectoryObject(key=Callback(DelMenu, feedObj=x), title="Remove Podcast", thumb = R(MINUS)))
		except:
			pass

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

	oc = ObjectContainer()
	oc.title1 = 'Select podcast to add'
	neary = str(query.replace (" ", "+"))
	pod = JSON.ObjectFromURL("https://itunes.apple.com/search?term=%s&entity=podcast&limit=25" % neary)['results']

	for x in pod:
		oc.add(DirectoryObject(key=Callback(MainMenu, urlofshow=[x][0]['feedUrl'], nameofshow=[x][0]['collectionName'], artofshow=[x][0]['artworkUrl600']), title=[x][0]['collectionName'], thumb=[x][0]['artworkUrl600']))

	return oc
