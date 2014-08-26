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
  </head>
  <body ng-controller="DirController">
    <div class="container">
        <h2>Dirshare</h2>
        <ol id="path-breadcrumb" class="breadcrumb">
            <li ng-click="setPath('/')""><a href="#">root</a></li>
            <li ng-repeat="p in nav_path"  ng-if="p[1] !== ''" class="active">
                <a href="#" ng-if="!$last" ng-click="setPath((p[0] || '') + '/' + p[1])">{{p[1]}}</a>
                <span ng-if="$last">{{p[1]}}</span>
            </li>
        </ol>

        <ul class="nav nav-pills">
            <li ng-repeat="dir in directories">
                <a class="pointer" ng-click="setPath(path + '/' + dir.name)">{{dir.name}}</a>
            </li>
            
            <li ng-if="basket.length > 0" ng-class="{active: in_basket}">
                <a class="pointer" ng-click="toggleInBasket()">
                    <span class="glyphicon glyphicon-transfer"></span>
                    <span class="badge">{{basket.length}}</span>
                </a>
            </li>
        </ul>

        <div ng-show="files.length > 0" id="page-selector">
            <div>
                <ul class="pagination pagination-sm">
                    <li ng-repeat="pa in pages" ng-click="setPage(pa)" ng-class="{active: $index == page}"><a href="#">{{pa+1}}</a>
                    </li>
                </ul>
            </div>
            <div class="btn-group btn-group-sm">
                <button ng-repeat="count in [5,15,30,50,200,500]" type="button" class="btn btn-default" ng-click="setPerPage(count)" ng-class="{active: per_page == count}" title="View {{count}} items per page">{{count}}</button>
            </div>
            
            <div class="btn-group btn-group-sm">
                <button ng-repeat="s in sizes.slice(1)" type="button" class="btn btn-default" ng-click="setSize(s)" ng-class="{active: size == s}" title="Change image size to {{s}}">{{s}}</button>
            </div>
            
            <div class="btn-group btn-group-sm">
                <button type="button" class="btn btn-default" ng-click="toggleExif()" ng-class="{active: show_exif}" title="Toggle EXIF information">Exif</button>
                <button type="button" class="btn btn-default" ng-click="toggleSelecting()" ng-class="{active: selecting}" title="Switch between select and view mode">Select mode</button>
                <button type="button" class="btn btn-default" ng-click="toggleScroll()" ng-class="{active: use_scroll}" title="Switch between scroll and grid display modes">Scroll</button>
            </div>
            <div class="btn-group btn-group-sm">
                <button type="button" class="btn btn-success" ng-click="dirws.zip(basket)" ng-if="basket.length > 0" title="Download zip of selected files"><span class="glyphicon glyphicon-compressed"></span></button>
            </div>
        </div>

        <div ng-if="!refreshing">
        
            <!-- scroller -->
            <div class="full-width xscroll-only" ng-show="use_scroll">
                <ul class="table xfull-width">
                    <li class="cell-thumbnail cell-middle pointer" ng-repeat="photo in displayed_images">
                        <img ng-src="{{dirws.thumbUrl(photo)}}" ng-click="clickImage(photo)" ng-class="{selected: inBasket(photo)}"/>
                    </li>
                </ul>
            </div>
            
           
            <!-- grid -->
            <div ng-if="image === ''" class="row" ng-show="!use_scroll">
                <div class="col-sm-2" ng-repeat="photo in displayed_images">
                    <a class="thumbnail pointer" ng-class="{selected: inBasket(photo)}">
                        <img ng-src="{{dirws.thumbUrl(photo)}}" ng-click="clickImage(photo)"/>
                    </a>
                </div>
            </div>

            <hr ng-if="image !== ''"> 
            <div ng-if="image !== ''" id="image-container" class="text-center row">
                <div ng-class="show_exif ? 'col-sm-6': 'col-sm-12'">
                    <!--<a ng-href="{{dirws.imageUrl(image, size)}}" target="_blank">-->
                    <a ng-click="clickImage('')">                    
                        <img ng-src="{{dirws.imageUrl(image, size)}}" class="full-width">
                    </a>
                </div>
                <div class="col-sm-6 panel" ng-show="show_exif">
                    <div class="panel-body">
                        <dl class="dl-horizontal">
                          <dt ng-repeat-start="(mkey, mvalue) in meta.exif">{{mkey}}</dt>
                          <dd ng-repeat-end>{{mvalue}}</dd>
                        </dl>
                    </div>
                </div>
            </div>
        </div>
            
        <div class="clearfix"></div>
        <hr>
        <p class="text-right italic-text">
            powered by <a href="https://github.com/joaoubaldo/dirshare">dirshare</a>
        </p>
        <script src="${request.static_url('dirshare:static/js/jquery-1.11.1.min.js')}"></script>
        <script src="${request.static_url('dirshare:static/js/bootstrap.min.js')}"></script>
        <script src="${request.static_url('dirshare:static/js/ui-bootstrap-0.11.0.min.js')}"></script>        
    </div>
  </body>
</html>
