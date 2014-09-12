angular.module("dirshareApp").controller(
"DirController",
["$scope", "$http", "$location", "$rootScope", "$timeout", "$element", "$anchorScroll", "dirws",
function($scope, $http, $location, $rootScope, $timeout, $element, $anchorScroll, dirws) {
    $scope.page = 0;
    $scope.per_page = 50;
    $scope.image = null;  // current image, '' to hide display
    $scope.meta = {};  // current image metadata
    $scope.path = '';  // current directory
    $scope.size = '';
    $scope.jobs = [];

    $scope.readyPath = true;  // is listDir() complete?
    $scope.readyMeta = false;  // is metadata complete?
    $scope.readyThumbs = true;  // are thumbs for path preloaded?

    $scope.selecting = false;
    $scope.showMetadata = false;
    $scope.showManage = false;
    $scope.use_scroll = true;  // use scroll? else grid
    $scope.dirws = dirws;
    $scope.basket = [];  // current set of images in basket (ex. to export)
    $scope.displayedImages = [];  // paths of images to be displayed
    $scope.images = {};  // current path images
    $scope.viewStack = ['browsing'];

    $scope.setPath = function (path) {
        $scope.path = dirws.cleanPath(path);
    };

    $scope.setSize = function (size) { $scope.size = size; };
    $scope.setPage = function (page) { $scope.page = page; };
    $scope.setPerPage = function (per_page) { $scope.per_page = per_page; };

    $scope.toggleExif = function () { $scope.showMetadata = !$scope.showMetadata; };
    $scope.toggleScroll = function () { $scope.use_scroll = !$scope.use_scroll; };
    $scope.toggleSelecting = function () { $scope.selecting = !$scope.selecting; };
    $scope.toggleManage = function () { $scope.showManage = !$scope.showManage; };

    $scope.currentView = function() {
        return $scope.viewStack[$scope.viewStack.length - 1];
    };

    $scope.isLoading = function() {
        return !$scope.readyPath || !$scope.readyThumbs;
    };

    $scope.hasDisplayedImages = function() {
        return $scope.displayedImages.length > 0;
    };

    $scope.refresh = function() {
        if ($scope.isLoading())
            return;

        $scope.readyPath = false;
        $scope.readyThumbs = false;
        $scope.images = {};
        $scope.displayedImages = [];
        $scope.thumbsLoaded = 0;

        dirws.listDir($scope.path, $scope.per_page, $scope.page).then(
            function(data) {
                /* save data keys to $scope */
                angular.forEach(data, function(value, key) {
                    if (key == 'path') {
                        $scope.setPath(value);
                    } else {
                        this[key] = value;
                    }
                },
                $scope);
                $scope.readyPath = true;
                if (data['files'].length < 1)
                    $scope.readyThumbs = true;
                var i = 0;
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
                    $scope.images[img.full_path] = img;

                    $timeout(function() {
                        var _load_thumb = dirws.preloadImage(img.full_path, img.thumb_url);
                        _load_thumb.then(function (res) {
                            if (!(res['id'] in $scope.images)) {
                                return;
                            }

                            $scope.images[ res['id'] ]['thumb_loaded'] = true;

                            var all_loaded = true;
                            angular.forEach($scope.images, function (value, key) {
                                if (!value['thumb_loaded']) {
                                    all_loaded = false;
                                    return;
                                }
                            });

                            $scope.thumbsLoaded += 1;

                            if (all_loaded) {
                                $scope.displayedImages = Object.keys($scope.images);
                                $scope.readyThumbs = true;
                            }
                        });
                    }, i*1);
                    i++;
                });
            }
        );
    };

    $scope.refreshImage = function() {
        if (!$scope.image)
            return;

        var size = $scope.size;
        if (!(size in $scope.images[$scope.image].sizes)) {
            $scope.images[$scope.image].sizes[size] = {
                'url': dirws.imageUrl($scope.image, size),
                'loaded': false
            }
        }

        if (!$scope.images[$scope.image].sizes[size].loaded) {
            var _load_image = dirws.preloadImage({'id': $scope.image, 'size': size}, $scope.images[$scope.image].sizes[size]['url']);
            _load_image.then(function(res) {
                $scope.images[res.id.id].sizes[res.id.size].loaded = true;
            });
        }

        if ($scope.showMetadata && !$scope.images[$scope.image].metadata.metadata) {
            var _load_metadata = $http.get(dirws.metaUrl($scope.image)).success(function(data) {
                $scope.images[$scope.image].metadata = data;
            });
        }
    };

    $scope.changeView = function (view) {
        var current = $scope.currentView();
        if (current == view) {
            if ($scope.viewStack.length > 1)  // if equal go back
                $scope.viewStack.pop();
        }
        else
            $scope.viewStack.push(view);
    };

    /* set current image or select it, depending on mode */
    $scope.clickImage = function (full_path) {
        if ($scope.selecting) {
            $scope.toFromBasket(full_path);  // select mode
        } else {
            $scope.image = full_path;  // set active
        }
    };


    $scope.hideImage = function() {
        $scope.image = null;
    };

    /* put/remove image in/from basket */
    $scope.toFromBasket = function (full_path) {
        if ($scope.inBasket(full_path)) {
            $scope.basket.splice( $scope.basket.indexOf(full_path), 1);
        } else {
            $scope.basket.push(full_path);
        }


    };

    /* checks if image is in basket */
    $scope.inBasket = function (full_path) {
        return $scope.basket.indexOf(full_path) != -1;
    };

    $scope.isEmptyExif = function () {
        if (!$scope.image)
            return true;

        return dirws.keyCount($scope.images[$scope.image].metadata.metadata) < 1;
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
    }

    $scope.showNextImage = function() {
        var index = $scope.displayedImages.indexOf($scope.image);
        if (index != -1) {
            if ((index+1) <= $scope.displayedImages.length-1) {
                $scope.image = $scope.images[ $scope.displayedImages[index + 1] ].full_path;
                $scope.$apply();
            }
        }
    };

    $scope.showPrevImage = function() {
        var index = $scope.displayedImages.indexOf($scope.image);
        if (index != -1) {
            if (index > 0) {
                $scope.image = $scope.images[ $scope.displayedImages[index - 1] ].full_path;
                $scope.$apply();
            }
        }
    };

    $scope.onKeyDown = function(event) {
        if (event.keyCode == 37)
            $scope.showPrevImage();
        else if (event.keyCode == 39)
            $scope.showNextImage();
    };

    /*
     *  ------------ Watches ------------
     */

    $scope.$watch("path", function(new_value, old_value) {
        if (new_value !== old_value) {

            if ($scope.currentView() == 'basket')
                $scope.viewStack.pop();
            $scope.refresh();
        }
    });


    $scope.$watch("basket", function(new_value, old_value) {
        if ($scope.basket.length < 1 && $scope.currentView() == 'basket') {
            $scope.changeView('basket');
            $scope.selecting = false;
        }
    },
    true);

    $scope.$watch("page", function(new_value, old_value) {
        if (new_value !== old_value) {
            $scope.refresh();
        }
    });

    $scope.$watch("per_page", function(new_value, old_value) {
        if (new_value !== old_value) {
            $scope.page = 0;
            $scope.refresh();
        }
    });

    $scope.$watch("image", function(new_value, old_value) {
        $scope.refreshImage();
    }, true);

    $scope.$watch("showMetadata", function(new_value, old_value) {
        $scope.refreshImage();
    });

    $scope.$watch("size", function(new_value, old_value) {
        $scope.refreshImage();
    });


    $scope.$watch("currentView()", function(new_value, old_value) {
        if ($scope.currentView() == 'basket') {
            $scope.displayedImages = $scope.basket;
        }
        else if ($scope.currentView() == 'browsing') {
            $scope.displayedImages = Object.keys($scope.images);
        }
    });

    /* Initial page load */
    dirws.setup().then(function(data) {
        $scope.setPath("/");
        $scope.size = data.sizes[1];

        var delay = 5000;
        var pollState = function() {
            $timeout(function() {
                delay = 5000;
                if ($scope.jobs.length > 0)
                    delay = 1000;

                dirws.getJobs().then(function(data) {
                    $scope.jobs = data['jobs'];
                });
                pollState();
            }, delay);
        };
        pollState();

        $element.bind("keydown", function (event) {
            $scope.onKeyDown(event);
        });
    });
}]);
