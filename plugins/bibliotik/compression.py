import zlib

BIBLIOTIK_ZDICT = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0" />
    <link rel="shortcut icon" href="/static/favicon.ico" />
    <script src="/static/jquery-1.7.2.min.js"></script>
    <script src="/static/jquery.confirm-1.2.js"></script>
    <script src="/static/formerrorlistscroll.js"></script>
    <script src="/static/lightbox/jquery.lightbox-0.5.min.js"></script>
    <script src="/static/jquery.lazy-1.7.4.min.js"></script>
    <script src="/static/imagesloaded-4.1.min.js"></script>
    <script src="/static/jquery.qtip-3.0.3.min.js"></script>
    <script src="/static/disableOnSubmit.js"></script>
    <script src='/static/simplemde-1.11.2.min.js'></script>
    <link rel='stylesheet' href='/static/simplemde-1.11.2.min.css'>
    <link rel='stylesheet' href='/static/components/font-awesome/font-awesome-built.css'>
    <link rel="stylesheet" type="text/css" media="screen" href="/static/lightbox/jquery.lightbox-0.5.css" />
    <link rel="stylesheet" type="text/css" media="screen" href="/static/jquery.qtip-3.0.3.min.css" />
    <link rel="stylesheet" type="text/css" media="screen" href="/static/default.css?" />
    <link rel="stylesheet" type="text/css" media="screen" href="/static/css_garden/makeup.css?" />
    <title>Bibliotik / Torrents / </title>
    <script type="text/javascript">
    document.head.parentElement.className += ' have-js'; // flag JS availability

    function brokenImage(img) {
        img.src="/static/icons/NI_Broken.png";
    }

    $(function() {
       $('a[rel*=lightbox]').lightBox({
        imageLoading: '/static/lightbox/lightbox-ico-loading.gif',
        imageBtnClose: '/static/lightbox/lightbox-btn-close.gif',
        imageBtnPrev: '/static/lightbox/lightbox-btn-prev.gif',
        imageBtnNext: '/static/lightbox/lightbox-btn-next.gif',
        imageBlank: '/static/lightbox/lightbox-blank.gif'
       });

       $('form').disableOnSubmit();

       $('time').attr('title', function() {
        return new Date($(this).attr('datetime')).toLocaleString();
       });

       // Rewrite legacy links as relative links
       $('a[href*="bibliotik.org"]').attr('href', function(idx, href){
           return (href||$(this).attr('href')).replace(/^https?:\/\/(www\.)?bibliotik.org/i, '');
       });

    });
    </script>
</head>
<body>

<div id="superwrap">
<div id="headerwrap">
<div id="pre_header">
    <ul id="pre_header_status">
        <li><a href=""></a> ()</li>
    	<li><a href="/settings">Settings</a></li>
        <li><a href="/logout?authkey=">Log Out</a></li>
		<li>Up: </li>
        <li>Down: </li>
        <li>			Ratio: 
						,</li>
		<li>Required: 0.0 (Exempt!)</li>
			    </ul>
    
    <ul id="pre_header_nav">
       
        <li><a href="/invites">Invites</a>
							(4)
			</li>
				<li>			<a href="/conversations">Conversations</a>
			</li>
        <li><a href="/notifications">Notifications</a></li>
        <li><a href="/bookmarks">Bookmarks</a></li>
        <li><a href="/uploads">Uploads</a></li>
    </ul>
</div>

<div id="header">
    <div id="header_top">
        <a href="/"><span id="header_logo"></span></a>

				
        <span id="header_notifications">
			        	        </span>
    </div>
    <div id="header_nav">
        <ul id="header_nav_links">
            <li><a href="/">Home</a></li>
            <li><a href="/torrents/">Torrents</a></li>
            <li><a href="/requests/">Requests</a></li>
            <li><a href="/collections/">Collections</a></li>
            <li><a href="/forums/">Forums</a></li>
            <li><a href="/rules/">Rules</a></li>
            <li><a href="/help/">Help</a></li>
            <li><a href="/log/">Log</a></li>
            <li><a href="/upload/">Upload</a></li>
        </ul>
        <span id="header_nav_search">
            <form action="/torrents/" method="get">
                <input type="text" size="35" name="search" id="search_header" value="> Search torrents" onblur="if (this.value == '') this.value = '> Search torrents';" onfocus="if (this.value == '> Search torrents') this.value = '';" />
                <input type="submit" value="" style="display:none;" />
            </form>
        </span>
    </div>
</div>
</div>
<div id="body">


<div id="torrent-" class="torrent retail ebooks-category epub-format english-language">

<h1 id="title"><img src="/static/icons/Ebooks.png"  style="vertical-align:text-top" title="Ebooks" />
    </h1>

<div id="sidebar">

<a rel="lightbox" href=""><img src='' width="220" /></a>

<ul>
    <li class="details_peers">
        <strong>7</strong> <a href="/torrents//peers">
		Peers
		</a>
    </li>

    <li class="details_snatches">
        <strong>5</strong> <a href="/torrents//snatches">
		Snatches
		</a>
    </li>

</ul>

<form action="" method="post" accept-charset="UTF-8"><input type="hidden" name="addTags" /><input type="hidden" name="authkey" value="" /><table><tr valign="top"><td class="Flabel"><label for="TagsField">Add tag: </label></td><td class="Ffield"><input type="text" name="TagsField" id ="TagsField" maxlength="1024" size ="10" value="" /></td></tr><tr><td colspan="2"><input type="submit" value="Add tag!" /></td></tr></table></form>
</div>

<div id="main">

<div id="detailsbox">

<p id="creatorlist">
    By <a class="authorLink" href="/creators/"></a></p>





<p id="published">
    Published by <a class="publisherLink" href="/publishers/"></a> in  (<span id="torrentISBN"></span>)</p>

<p id="details_content_info">
    English, pages</p>

<p id="details_tags">
        Tags: <span class="taglist"><a class="tagLink" href="/tags/26">fiction</a></span>    </p>

<p id="details_file_info">
    Retail EPUB,
     MB,
     file(s)
    <a><label for=file-toggler class=toggling data-show="(show)" data-hide="(hide)">(show)</label></a>
</p>


<p id="details_upload_info">
        Uploaded by <a href="/users/"></a>        <time datetime=""> minutes,  seconds ago</time>
</p>


<p id="details_activity_info">
     seeders,
     leecher,
     snatches,
    <a href="/torrents/#comments">0</a>
     comments,
    0 bookmarks
</p>



<p id="details_ratio_info">
	<em>If you download this torrent, your ratio will be .</em>
</p>

<p id="details_links">
<a href="/torrents//download" title="Download"><img src="/static/icons/download.png" /></a>

	<span class="doBookmark" title="Add Bookmark">&nbsp;</span>
<a href="/torrents//report" title="Report"><img src="/static/icons/report.png" /></a>
	<a href="/torrents//wiki" title="Description"><img src="/static/icons/wiki.png" /></a>
	<a href="/torrents//images" title="Images"><img src="/static/icons/image.png" /></a>
</p>


</div>

<input type=checkbox id=file-toggler class=toggling>
<div id="files" class="table_div toggling">
<h2>Files</h2>
<table cellspacing="0" style="width:auto">
<thead>
<tr>
    <th>Filename</th>
    <th>Size</th>
</tr>
</thead>
<tbody>
<tr>
    <td>/td>
    <td> MB</td>
</tr>
</tbody>
</table>
</div>

<div id="description">
<h2>Description</h2>
    <div class="markdown">
</div>
</div>

</div>


<div id="comments">

<script type="text/javascript">
    $(function() {
        $('.quoteComment').live("click", function() {
            var commentId = $(this).attr("id").split("-")[1];
            $.ajax({
                method: "get",
                url: "/torrents//comments/" + commentId + "/get",
                beforeSend: function() {
                    $("#doQuoteComment-" + commentId).html('<img src="/static/icons/loading.gif" />');
                },
                complete: function() {
                    $("#doQuoteComment-" + commentId).html('<a class="quoteComment" id="quote-' + commentId + '">Quote</a>');
                },
                success: function(text) {
                    var temp = $("#CommentField").val();
                    if (temp.length && !temp.endsWith('\n')) temp += '\n';
                    if (temp.length && !temp.endsWith('\n\n')) temp += '\n';
                    temp += text + '\n\n';
                    $("#CommentField").val(temp);
                    $("#CommentField").change();
                    window.location.hash = "#commentHeader";
                },
                error: function() {
                    $("#doQuoteComment-" + commentId).html('<strong>Connection failed!</strong>');
                }
            });
        });
    });
</script>

<h2>Comments</h2>


<p>No comments found.</p>
</div>

<h4 id="commentHeader">Add comment</h4>
<form action="" method="post" accept-charset="UTF-8"><input type="hidden" name="addComment" /><input type="hidden" name="authkey" value="" /><table><tr><td class="Flabel"><label for="CommentField">Comment: </label></td><td class="Ffield"><textarea name="CommentField" id="CommentField" rows="15" cols="90"></textarea></td></tr><tr><td colspan="2"><input type="submit" value="Add comment!" /></td></tr></table></form></div>
</div> <!-- End #body -->

<div id="footer">

<div id="footer_nav">
	<div id="more">
    	<h4>More:</h4>
        <ul>
            <li><a href="/users">Users</a></li>
            <li><a href="/tags">Tags</a></li>
            <li><a href="/creators">Creators</a></li>
            <li><a href="/publishers">Publishers</a></li>
											</ul>
	</div>
	<div id="rules">
        <h4>Rules:</h4>
        <ul>
			<li><a href="/rules">Main</a></li>
			<li><a href="/rules/uploading">Uploading</a></li>
			<li><a href="/rules/retail">Retail</a></li>
			<li><a href="/rules/trumping">Trumping</a></li>
			<li><a href="/rules/naming-conventions">Naming</a></li>
			<li><a href="/rules/requests">Requests</a></li>
			<li><a href="/rules/tagging">Tagging</a></li>
			<li><a href="/rules/ratio">Ratio</a></li>
        </ul>
    </div>
    <div id="help">
        <h4>Help:</h4>
		<ul>
			<li><a href="/tutorials">Tutorials</a></li>
			<li><a href="/help/contact">Contact</a></li>
			<li><a href="/help/classes">User Classes</a></li>
			<li><a href="/help/searching">Searching</a></li>
			<li><a href="/help/editor">Text Formatting</a></li>
			<li><a href="/help/clients">Allowed Clients</a></li>
			<li><a href="/help/ports">Blacklisted Ports</a></li>
		</ul>
	</div>
</div>


</div> <!-- End #footer -->

</div> <!-- End #superwrap -->
<script src='/static/store-2.0.3.everything.min.js'></script><script src='/static/toggle-display.js?'></script><script type='text/javascript'>var bookmarksAuthKey = "";</script><script src='/static/do-bookmarks.js?'></script><script src='/static/cover-hover.js?'></script><script src='/static/wysiwyg-editor.js?'></script></body>
</html>'''.encode()


def bibliotik_compress_html(html):
    obj = zlib.compressobj(level=9, zdict=BIBLIOTIK_ZDICT)
    return b'b\x01' + obj.compress(html.encode()) + obj.flush()


def bibliotik_decompress_html(data):
    if data[:2] == b'<!':
        return data.decode()
    if data[:2] == b'b\x01':
        obj = zlib.decompressobj(zdict=BIBLIOTIK_ZDICT)
        decompressed_data = obj.decompress(data[2:]) + obj.flush()
        return decompressed_data.decode()
    else:
        raise Exception('Unknown/invalid Bibliotik compression header')
