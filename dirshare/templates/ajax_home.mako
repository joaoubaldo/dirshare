<!DOCTYPE html>
<html ng-app="dirshareApp">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="dirshare - an application to quickly share a directory of images">
    <meta name="author" content="Joao Coutinho">
    <title>dirshare</title>
    <link href="${request.static_url('dirshare:static/css/theme.css')}" rel="stylesheet">
    <link href="${request.static_url('dirshare:static/css/bootstrap.min.css')}" rel="stylesheet">
    <script src="${request.static_url('dirshare:static/js/angular.min.js')}"></script>
    <script src="${request.static_url('dirshare:static/js/app.js')}"></script>
    <script src="${request.static_url('dirshare:static/js/services.js')}"></script>
    <script src="${request.static_url('dirshare:static/js/controllers.js')}"></script>
  </head>
  <body ng-controller="DirController">
    <div class="container">
        <ol id="path-breadcrumb" class="breadcrumb">
            <li ng-click="setPath('/')"><a href="#"><span class="glyphicon glyphicon-home"></span></a></li>
            <li ng-repeat="p in nav_path" ng-if="p[1]" class="active" ng-if="readyPath">
                <a href="#" ng-if="!$last" ng-click="setPath((p[0] || '') + '/' + p[1])">
                    <span class="glyphicon glyphicon-folder-open">&nbsp;</span>
                    {{p[1]}}</a>
                <span ng-if="$last"><span class="glyphicon glyphicon-folder-close">&nbsp;</span>{{p[1]}} <span class="badge" ng-if="image_count > 0">{{image_count}}</span></span>
            </li>
        </ol>


        <!-- path select : pills -->
        <ul class="nav nav-pills" ng-if="readyPath">
            <li ng-repeat="dir in directories" class="pointer">
                  <a ng-click="setPath(path + '/' + dir.name)">{{dir.name}}</a>
             </li>
        </ul>

        <!-- buttons -->
        <div>

            <!-- path selector -->
            <!--<div class="btn-group pointer" ng-if="directories.length > 0">
              <button class="btn btn-primary btn-sm dropdown-toggle" type="button" data-toggle="dropdown">
                {{nav_path[nav_path.length-1][1] || '/' }} <span class="caret"></span>
              </button>
              <ul class="dropdown-menu" role="menu">
                  <li ng-repeat="dir in directories">
                      <a ng-click="setPath(path + '/' + dir.name)">{{dir.name}}</a>
                  </li>
              </ul>
            </div>-->

            <!-- page selector -->
            <div class="btn-group pointer"  ng-if="!isLoading() && hasDisplayedImages()">
              <button class="btn btn-default btn-sm dropdown-toggle" type="button" data-toggle="dropdown">
                page {{page+1}} <span class="caret"></span>
              </button>
              <ul class="dropdown-menu" role="menu">
                <li ng-repeat="pa in pages" ng-click="setPage(pa)" ng-class="{active: $index == page}"><a>{{pa+1}}</a>
              </ul>
            </div>

            <!-- per page selector -->
            <div class="btn-group pointer"  ng-if="!isLoading() && hasDisplayedImages()">
              <button class="btn btn-default btn-sm dropdown-toggle" type="button" data-toggle="dropdown">
                x {{per_page}} <span class="caret"></span>
              </button>
              <ul class="dropdown-menu" role="menu">
                  <li ng-repeat="count in [10,50,200,500]" ng-click="setPerPage(count)" ng-class="{active: per_page == count}" title="View {{count}} items per page"><a>{{count}}</a></li>
              </ul>
            </div>

            <!-- size selector -->
            <div class="btn-group pointer"  ng-if="!isLoading() && hasDisplayedImages()">
              <button class="btn btn-default btn-sm dropdown-toggle" type="button" data-toggle="dropdown">
                {{size}} <span class="caret"></span>
              </button>
              <ul class="dropdown-menu" role="menu">
                  <li ng-repeat="s in sizes.slice(1)" ng-click="setSize(s)" ng-class="{active: size == s}" title="Change image size to {{s}}"><a>{{s}}</a></li>
              </ul>
            </div>

            <!-- toggles -->
            <div class="btn-group btn-group-sm" ng-if="!isLoading()">
                <button type="button" class="btn btn-default" ng-click="toggleMetadata()" ng-class="{active: showMetadata}" title="Toggle EXIF information" ng-if="basket.length > 0 || hasDisplayedImages()">Meta</button>
                <button type="button" class="btn btn-default" ng-click="toggleScroll()" ng-class="{active: useScroll}" title="Switch between scroll and grid display modes" ng-if="basket.length > 0 || hasDisplayedImages()">Scroll</button>
                <button type="button" class="btn btn-default" ng-click="toggleManage()" ng-class="{active: showManage}" title="Toggle managing panel">Manage</button>
            </div>

            <!-- select options -->
            <div class="btn-group" ng-if="!isLoading()">
              <button type="button" class="btn btn-sm btn-default" ng-click="toggleSelecting()" ng-class="{active: selecting}" title="Switch between select and view mode" ng-if="basket.length > 0 || hasDisplayedImages()"><span class="badge" ng-if="basket.length > 0">{{basket.length}}</span> Select</button>
              <button type="button" class="btn btn-sm btn-default dropdown-toggle" data-toggle="dropdown" ng-if="basket.length > 0">
                <span class="caret"></span>
                <span class="sr-only">Toggle Dropdown</span>
              </button>
              <ul class="dropdown-menu pointer" role="menu" ng-if="basket.length > 0">
                <li ng-click="changeView('basket')" ng-if="basket.length > 0" ng-class="{active: currentView()=='basket'}" title="Toggle view of selected images"><a><span class="glyphicon glyphicon-transfer"></span> Review</a></li>
                <li ng-click="dirws.zip(basket)" ng-if="basket.length > 0" title="Download zip of selected files"><a><span class="glyphicon glyphicon-compressed"></span> Zip</a></li>
              </ul>
            </div>

        </div>

        <!-- manage panel -->
        <div class="panel panel-default" id="manage" ng-if="showManage">
            <div class="panel-heading"><span class="glyphicon glyphicon-cog"></span>Manage</div>
            <div class="panel-body">
                <button disabled type="button" class="btn btn-default" ng-click="rebuild(path)"><span class="glyphicon glyphicon-refresh">&nbsp;</span>Rebuild cache</button>
                <button type="button" class="btn btn-warning" ng-click="debugScope()"><span class="glyphicon glyphicon-bullhorn">&nbsp;</span>Debug $scope</button>
            </div>
        </div>

        <!-- body -->
        <div>

            <!-- scroller -->
            <div class="full-width xscroll-only" ng-if="useScroll && readyThumbs" id="scroll-view">
                <ul class="table xfull-width">
                    <li class="cell-thumbnail cell-middle pointer" ng-repeat="img in displayedImages" ng-click="clickImage(img)" ng-class="{selected: img == image}">
                        <img ng-src="{{dirws.thumbUrl(img)}}" ng-class="{selected: inBasket(img) && selecting}" id="{{img}}"/>
                    </li>
                </ul>
            </div>

            <!-- grid -->
            <div class="row" ng-if="!useScroll && image == null && readyThumbs">
                <div class="col-sm-2" ng-repeat="img in displayedImages" ng-click="clickImage(img)">
                    <a class="thumbnail pointer" ng-class="{selected: inBasket(img) && selecting}">
                        <img ng-src="{{dirws.thumbUrl(img)}}" id="{{img}}"/>
                    </a>
                </div>
            </div>

            <!-- progress bar -->
            <div class="row" ng-if="!readyThumbs && files_paths.length > 0">
                <hr>
                <div class="progress">
                  <div class="progress-bar" role="progressbar" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100" ng-style="{width: (displayedImages.length/files_paths.length)*100+'%'}">
                    {{displayedImages.length}}
                  </div>
                </div>
            </div>

        </div>

        <div ng-if="isLoading() || (image && isImageLoading)" class="text-center">
            <img src="${request.static_url('dirshare:static/loader.gif')}" />
        </div>

        <div ng-if="image && images.sizeLoaded(image, size)">
            <div id="image-container" class="text-center row">
                <div ng-class="(showMetadata && images.hasMetadata(image)) ? 'col-sm-6': 'col-sm-12'">
                    <a ng-click="hideImage()">
                        <img ng-src="{{images.getSizeUrl(image, size)}}" class="full-width">
                    </a>
                </div>
                <div class="col-sm-6 panel" ng-show="showMetadata && images.hasMetadata(image)">
                    <div class="panel-body">
                        <dl class="dl-horizontal">
                          <dt ng-repeat-start="(mkey, mvalue) in images.getMetadata(image)">{{mkey}}</dt>
                          <dd ng-repeat-end>{{mvalue}}</dd>
                        </dl>
                    </div>
                </div>

            </div>

            <ul class="pager" id="prev-next-nav" ng-if="readyThumbs">
              <li><a href="#" ng-click="showPrevImage()" ng-if="hasPrevImage()">Previous</a></li>
              <li><a href="#" ng-click="showNextImage()" ng-if="hasNextImage()">Next</a></li>
            </ul>
        </div>

        <div class="clearfix"></div>
        <hr>
        <p class="text-right italic-text">
            dirshare <a href="https://github.com/joaoubaldo/dirshare" target="_blank">github</a> | <a href="http://b.joaoubaldo.com" target="_blank">blog</a>
        </p>
        <script src="${request.static_url('dirshare:static/js/jquery-1.11.1.min.js')}"></script>
        <script src="${request.static_url('dirshare:static/js/bootstrap.min.js')}"></script>
        <script src="${request.static_url('dirshare:static/js/ui-bootstrap-0.11.0.min.js')}"></script>        
    </div>
  </body>
</html>
