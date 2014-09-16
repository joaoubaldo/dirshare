angular.module("dirshareApp").controller(
"DirController",
["$scope", "$http", "$location", "$rootScope", "$timeout", "$element", "$anchorScroll", "dirws", "images",
function($scope, $http, $location, $rootScope, $timeout, $element, $anchorScroll, dirws, images) {

    /* Properties */
    $scope.dirws = dirws;  // service
    $scope.images = images;  // service

    $scope.page = 0;  // current page
    $scope.per_page = 50;  // images per page
    $scope.image = null;  // current image, '' to hide display
    $scope.path = '';  // current directory
    $scope.size = '';  // current size

    $scope.readyPath = true;  // is listDir() complete?
    $scope.readyThumbs = true;  // are thumbs for path preloaded?
    $scope.isImageLoading = false;  // selected image preloaded?

    $scope.files_paths = [];  // list of full_paths for current path (from py)
    $scope.selecting = false;  // Select mode
    $scope.showMetadata = false;  // Show metadata?
    $scope.showManage = false;  // Show manage panel?
    $scope.useScroll = true;  // Use scroll layout? Else grid
    $scope.basket = [];  // current set of images in basket (ex. to export)
    $scope.displayedImages = [];  // paths of images to be displayed
    $scope.viewStack = ['browsing'];  // Stack of views. Last item is current
    $scope.listDirTimer = 0;
    $scope.loadImageTimer = 0;
    $scope.listTimeout = 2000;
    $scope.imageTimeout = 5000;

    /* Methods */

    $scope.setPath = function (path) {
        if ($scope.isLoading())
            return;
        $scope.path = dirws.cleanPath(path);

        if ($scope.currentView() == 'basket')
            $scope.viewStack.pop();

        $scope.refreshPath();
    };

    $scope.setSize = function (size) {
        $scope.size = size;
        $scope.setImage($scope.image);
    };

    $scope.setPage = function (page) {
        $scope.page = page;
        $scope.refreshPath();
    };

    $scope.setPerPage = function (per_page) {
        $scope.per_page = per_page;
        $scope.page = 0;
        $scope.refreshPath();
    };

    $scope.toggleMetadata = function () {
        $scope.showMetadata = !$scope.showMetadata;

        if ($scope.image && $scope.showMetadata)
            images.cacheMetadata($scope.image, function() {
                $scope.$apply();
            });
    };

    $scope.toggleScroll = function () {
        $scope.useScroll = !$scope.useScroll;
    };

    $scope.toggleSelecting = function () {
        $scope.selecting = !$scope.selecting;
    };

    $scope.toggleManage = function () {
        $scope.showManage = !$scope.showManage;
    };

    $scope.currentView = function() {
        return $scope.viewStack[$scope.viewStack.length - 1];
    };

    $scope.isLoading = function() {
        return !$scope.readyPath || !$scope.readyThumbs;
    };

    $scope.hasDisplayedImages = function() {
        return $scope.displayedImages.length > 0;
    };

    $scope.refreshPath = function() {
        if ($scope.isLoading())
            return;

        function doRequest() {
            $scope.readyPath = false;
            $scope.readyThumbs = false;
            $scope.displayedImages = [];
            $scope.files_paths = [];
            $scope.listDirTimer = new Date().getTime();
            dirws.listDir(
                $scope.path,
                $scope.per_page,
                $scope.page).then(
                    processListDirResult
                );

            _waitForThumbs();
        }

        function _waitForThumbs() {
            var timeout = $scope.listTimeout;

            if (!$scope.readyThumbs) {
                var now = new Date().getTime();
                if ( (now - $scope.listDirTimer) > timeout) {
                    doRequest();
                } else {
                    $timeout(_waitForThumbs, 500);
                }
            }

        }

        doRequest();
    };


    $scope.changeView = function (view) {
        var current = $scope.currentView();
        if (current == view) {
            if ($scope.viewStack.length > 1)  // if equal go back
                $scope.viewStack.pop();
        }
        else
            $scope.viewStack.push(view);

        if ($scope.currentView() == 'basket') {
            $scope.displayedImages = $scope.basket;
        }
        else if ($scope.currentView() == 'browsing') {
            $scope.displayedImages = $scope.files_paths;
        }
    };

    /* set current image or select it, depending on mode */
    $scope.clickImage = function (full_path) {
        if ($scope.selecting) {
            $scope.toFromBasket(full_path);  // select mode
        } else {
            $scope.setImage(full_path);  // set active
        }
    };

    $scope.setImage = function (full_path) {
        if ($scope.isImageLoading)
            return;

        if ($scope.image && images.sizeLoaded($scope.image, $scope.size))
            $scope.image = full_path;
        else if(!$scope.image)
            $scope.image = full_path;

        function doRequest() {
            if ($scope.image) {
                $scope.isImageLoading = true;
                $scope.loadImageTimer = new Date().getTime();
                images.cacheSized(
                    $scope.image,
                    $scope.size,
                    function () {
                        $scope.$apply();
                    }
                );
                if ($scope.showMetadata)
                    images.cacheMetadata($scope.image, function() {
                        $scope.$apply();
                    });
                _waitForImage();
            }
        }

        function _waitForImage() {
            var timeout = $scope.imageTimeout;

            /* Load metadata if needed */
            var metaReady = true;
            if ($scope.showMetadata)
                metaReady = images.hasMetadata($scope.image);

            var sizeLoaded = images.sizeLoaded($scope.image, $scope.size);
            if (!sizeLoaded || !metaReady) {
                var now = new Date().getTime();
                if ( (now - $scope.loadImageTimer) > timeout) {
                    doRequest();
                } else {
                    $timeout(_waitForImage, 50);
                }
            } else {
                $scope.isImageLoading = false;
                $location.hash("image-container");
                $anchorScroll();
            }
        }

        doRequest();
    };

    $scope.hideImage = function() {
        $location.hash($scope.image);
        $scope.image = null;
        $anchorScroll();
    };

    /* put/remove image in/from basket */
    $scope.toFromBasket = function (full_path) {
        if ($scope.inBasket(full_path)) {
            $scope.basket.splice( $scope.basket.indexOf(full_path), 1);
        } else {
            $scope.basket.push(full_path);
        }

        if ($scope.basket.length < 1 && $scope.currentView() == 'basket') {
            $scope.changeView('basket');
            $scope.selecting = false;
        }
    };

    /* checks if image is in basket */
    $scope.inBasket = function (full_path) {
        return $scope.basket.indexOf(full_path) != -1;
    };

    $scope.rebuild = function(path) {
        dirws.rebuild(dirws.cleanPath(path));
    };

    $scope.hasNextImage = function() {
        var index = $scope.displayedImages.indexOf($scope.image);
        if (index != -1)
            if ((index+1) <= $scope.displayedImages.length-1)
                return true;
        return false;
    };

    $scope.hasPrevImage = function() {
        var index = $scope.displayedImages.indexOf($scope.image);
        if (index != -1)
            if (index > 0)
                return true;
        return false;
    };

    $scope.showNextImage = function() {
        var index = $scope.displayedImages.indexOf($scope.image);
        if (index != -1) {
            if ((index+1) <= $scope.displayedImages.length-1) {
                $scope.setImage(images.getImage($scope.displayedImages[index+1]).full_path);
                $scope.$apply();  // FIX: this is bad, causing errors
            }
        }
    };

    $scope.showPrevImage = function() {
        var index = $scope.displayedImages.indexOf($scope.image);
        if (index != -1) {
            if (index > 0) {
                $scope.setImage(images.getImage($scope.displayedImages[index-1]).full_path);
                $scope.$apply();  // FIX: this is bad, causing errors
            }
        }
    };

    $scope.onKeyDown = function(event) {
        if (event.keyCode == 37)
            $scope.showPrevImage();
        else if (event.keyCode == 39)
            $scope.showNextImage();
    };

    $scope.debugScope = function() {
        console.log($scope)
    };


    /* Initial page load */
    function initialSetup() {
        dirws.setup().then(function (data) {
            $scope.setPath("/");
            $scope.size = data.sizes[1];
            $element.bind("keydown", function (event) {
                $scope.onKeyDown(event);
            });
        });
    };

    initialSetup();


    function processListDirResult(data) {
        $scope.setPath(data['path']);
        $scope.nav_path = data['nav_path'];
        $scope.pages = data['pages'];
        $scope.thumbnail_size = data['thumbnail_size'];
        $scope.sizes = data['sizes'];
        $scope.directories = data['directories'];
        $scope.files = data['files'];
        $scope.image_count = data['image_count'];
        $scope.page = data['page'];
        $scope.files_paths = data['files_paths'];

        $scope.readyPath = true;

        if (data['files'].length < 1)
            $scope.readyThumbs = true;


        /* Preload thumbnails */

        angular.forEach(data['files'], function(value, key) {
            var img = {
                'path': $scope.path,
                'metadata': {},
                'full_path': $scope.path + value['name'],
                'name': value['name'],
                'thumb_url': dirws.thumbUrl($scope.path + value['name']),
                'thumb_loaded': false,
                'sizes': {}
            };

            images.save(img.full_path, img);

            images.cacheThumbnail(img.full_path, function(image) {
                if (image.path != $scope.path) {
                    return;
                }
                $scope.displayedImages.push(image.full_path);
                if ($scope.displayedImages.length == $scope.files_paths.length) {
                    $scope.readyThumbs = true;
                    console.log("Preload complete", $scope.path);
                }
                $scope.listDirTimer = new Date().getTime();
                $scope.$apply();
            }); //  - cacheThumbnail

        });
    };

}]);
