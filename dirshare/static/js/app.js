var app = angular.module("dirshareApp", []);

app.factory(
'dirws', 
['$http', '$q', '$window', function($http, $q, $window) {
    var service = {
        config: {},
        
        setConfig: function(data) { this.config = data; },
 
        /* thumbUrl(path) */
        thumbUrl : function(path) {
            var url = this.config.stream_url.replace("__PATH__", path).
                replace("__SIZE__", this.config.thumb_size);
            return url;
            },
        
        /* metaUrl(path) */
        metaUrl : function(path) {
            return this.config.meta_url.replace("__PATH__", path);
            },

        /* imageUrl(path, size) */
        imageUrl : function(path, size) {
            var url = this.config.stream_url.replace("__PATH__", path).
                replace("__SIZE__", size);
            return url;
            },
            
        /* zipUrl(files) */
        zipUrl : function(files) {
            var url = this.config.stream_url.replace("__FILES__", files);
            return url;
            },
        
        listDir : function(path, per_page, page) {
            var deffered = $q.defer();
            
            var url = this.config.listdir_url.
                replace("__PATH__", path).
                replace("__PERPAGE__", per_page).
                replace("__PAGE__", page);

            $http.get(url).success(function(data) {
                deffered.resolve(data);
                });
                
            return deffered.promise;
            },
            
        zip : function(files) {
            var url = this.config.zip_url.
                replace("__FILES__", JSON.stringify(files));
            $window.location.href = url;
            },

        keyCount : function(obj) {
            var count = 0;
            for(var key in obj) {
                if (obj.hasOwnProperty(key)) {
                    ++count;
                }
            }
            return count;
        },
            
        setup: function() {
            var obj = this;
            var deffered = $q.defer();
            
            $http.get("app/setup").success(function(data) {
                obj.setConfig(data);
                deffered.resolve(data);
                });
                
            return deffered.promise;
            }
    };
    
    return service;
}]);
  



app.controller(
"DirController", 
["$scope", "$http", "$location", "$rootScope", "$timeout", "dirws",
function($scope, $http, $location, $rootScope, $timeout, dirws) {
                
    function refresh() {
        $scope.refreshing = true;
        dirws.listDir($scope.path, $scope.per_page, $scope.page).then(
        function(data) {
            angular.forEach(data, function(value, key) {
                this[key] = value;
                },
            $scope);

            $scope.displayed_images = [];
            angular.forEach(data['files'], function(value, key) {
                $scope.displayed_images.push(data['path'] + '/'+ value['name'])
                });
            
            $scope.refreshing = false;
        });
    }

    /*$scope.toHash = function() {
        $location.hash(angular.toJson({
            'image': $scope.image,
            'per_page': $scope.per_page,
            'page': $scope.page,
            'path': $scope.path,
            'size': $scope.size,
            'show_exif': $scope.show_exif,
            'selecting': $scope.selecting,
            'use_scroll': $scope.use_scroll,
            'view_stack': $scope.view_stack,
            'basket': $scope.basket,
        }));
    };
    
    $scope.fromHash = function() {
        if ($location.hash() == "")
            return false;
        h = angular.fromJson($location.hash());
        $scope.per_page = h['per_page'];
        $scope.page = h['page'];
        $scope.size = h['size'];
        $scope.view_stack = h['view_stack'];
        $scope.basket = h['basket'];
        $scope.show_exif = h['show_exif'];
        $scope.selecting = h['selecting'];
        $scope.use_scroll = h['use_scroll'];

        $scope.path = h['path'];
        $scope.image = h['image'];
        console.log(h);
        return true;
    };*/
    
    $scope.page = 0;
    $scope.per_page = 30;
    $scope.image = '';
    $scope.meta = {};
    $scope.path = '';
    $scope.size = '';
    $scope.data = {};
    $scope.refreshing = true;
    $scope.selecting = false;
    $scope.show_exif = false;
    $scope.use_scroll = true;
    $scope.dirws = dirws;
    $scope.basket = [];  // current set of images in basket (ex. to export)
    $scope.displayed_images = [];  // current set of images to be displayed
    $scope.view_stack = ['browsing'];


    $scope.setPath = function (path) { $scope.path = path; };
    $scope.setSize = function (size) { $scope.size = size; };
    $scope.setPage = function (page) { $scope.page = page; };
    $scope.setPerPage = function (per_page) { $scope.per_page = per_page; };
   
    $scope.toggleExif = function () { $scope.show_exif = !$scope.show_exif; };
    $scope.toggleScroll = function () { $scope.use_scroll = !$scope.use_scroll; };
    $scope.toggleSelecting = function () { $scope.selecting = !$scope.selecting; };

    $scope.currentView = function() {
        return $scope.view_stack[$scope.view_stack.length - 1];
    }

    $scope.changeView = function (view) {
        var current = $scope.currentView();
        if (current == view) {
            if ($scope.view_stack.length > 1)  // if equal go back
                $scope.view_stack.pop();
        }
        else
            $scope.view_stack.push(view);
    };

    /* set current image or select it, depending on mode */
    $scope.clickImage = function (image) {
        if (image == "")
            $scope.image = "";   // clear
        else if ($scope.selecting) {
            $scope.toFromBasket(image);  // select mode
        } else
            $scope.image = image;  // set active
    };

    /* put/remove image in/from basket */
    $scope.toFromBasket = function (image) {
        var index = $scope.basket.indexOf(image);
        if (index != -1)
            $scope.basket.splice(index, 1);
        else
            $scope.basket.push(image);
    };

    /* checks if image is in basket */
    $scope.inBasket = function (image) {
        var index = $scope.basket.indexOf(image);
        return index != -1;
    };

    $scope.isEmptyExif = function () {
        return dirws.keyCount($scope.meta.metadata) < 1;
    };


    /*
     *  ------------ Watches ------------
     */

    $scope.$watch("path", function(new_value, old_value) {
        if (new_value !== old_value) {
            if ($scope.currentView() == 'basket')
                $scope.view_stack.pop();
            refresh();
        }
    });
    
    $scope.$watch("page", function(new_value, old_value) {
        if (new_value !== old_value) {
            refresh();
        }
    });

    $scope.$watch("per_page", function(new_value, old_value) {
        if (new_value !== old_value) {
            $scope.page = 0;
            refresh();
        }
    });

    $scope.$watch("basket.length", function(new_value, old_value) {
        if ($scope.basket.length < 1 && $scope.currentView() == 'basket') {
            $scope.changeView('basket');
            $scope.selecting = false;
        }
    });

    $scope.$watch("image", function(new_value, old_value) {
        if (new_value !== old_value && new_value != "") {
            $scope.refreshing = true;
            url = dirws.metaUrl(new_value);
            $http.get(url).
                success(function(data, status, headers, config) {
                    $scope.meta = data;
                    $scope.refreshing = false;
                });
        } else if ($scope.image == "") {
        }
    });
    
    $scope.$watch("currentView()", function(new_value, old_value) {
        if (new_value == old_value) return;
        if ($scope.currentView() == 'basket') {
            $scope.displayed_images = $scope.basket;
        }
        else if ($scope.currentView() == 'browsing') {
            $scope.displayed_images = [];
            angular.forEach($scope.files, function(value, key) {
                $scope.displayed_images.push($scope.path + '/'+ value['name'])
                });
        }
    });

    /* Initial page load */
    dirws.setup().then(function(data) {
        $scope.path = '/';  // trigger listDir
        $scope.size = data.sizes[1];
    });
}]);
