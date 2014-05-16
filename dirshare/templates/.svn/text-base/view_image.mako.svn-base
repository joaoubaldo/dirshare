<%inherit file="base.mako"/>

<h2>
    % for parent, p in nav_path:
        /<a href="${request.route_url('home', _query={'d': '/'.join((parent or '',p))})}">${p}</a>
    % endfor
</h2>

<div id="image-container">
    <img src="${request.route_url('stream_image', size=size, _query={'d': path})}"/>
</div>

% for idx, s in enumerate(sizes[1:]):
    <a href="${request.route_url('view_image', size=s, _query={'d': path})}">${s}</a>
% endfor


<ul id="thumb-navigation">
% for (isdir, c) in siblings:
    % if not isdir:
        <li>
            <a href="${request.route_url('view_image', size=sizes[1], _query={'d': "%s/%s" % (dir, c)})}"><img src="${request.route_url('stream_image', size=thumbnail_size, _query={'d': "%s/%s" % (dir, c)})}"></a>
        </li>            
    % endif
% endfor
</ul>
