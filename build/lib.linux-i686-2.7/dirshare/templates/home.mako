<%inherit file="base.mako"/>

<p id="path-breadcrumb">
    <a href="${request.route_url('home')}">root</a>
    % for parent, p in nav_path:
        /<a href="${request.route_url('home', _query={'d': '/'.join((parent or '',p))})}">${p}</a>
    % endfor
</p>

% if image_count:
<ul id="page-selection">
    % for p in pages:
    <li><a href="${request.route_url('home', _query={'d': path, 'p': p, 'pp': per_page})}">[${p + 1}]</a></li>
    % endfor
</ul>
% endif



<ul id="dir-list">
% for (isdir, c) in contents:
    % if isdir:
        <li><a href="${request.route_url('home', _query={'d': "%s/%s" % (path, c)})}">${c}</a>
    % endif
% endfor
</ul>

<ul id="photo-grid">
% for (isdir, c) in contents:
    % if not isdir:
        <li>
            <a href="${request.route_url('view_image', size=sizes[1], _query={'d': "%s/%s" % (path, c)})}"><img src="${request.route_url('stream_image', size=thumbnail_size, _query={'d': "%s/%s" % (path, c)})}"></a>
        </li>            
    % endif
% endfor
</ul>

<div style="clear: both;"/>
% if image_count:
<p><a href="${request.route_url('zip_page', _query={'d': path, 'p': page, 'pp': per_page})}">zip page</a></p>
% endif
