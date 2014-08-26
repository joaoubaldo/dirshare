var app = angular.module("dirshareApp", []);

app.factory(
'dirws', 
['$http', '$q', '$window', function($http, $q, $window) {
    var service = {
        config: {},
        
        setConfig: function(data) { this.config = data; },
 
        /* thumbUrl(path) */
        thumbUrl : function(path) {
            url = this.config.stream_url.replace("__PATH__", path).
                replace("__SIZE__", this.config.thumb_size);
            return url;
            },
        
        /* metaUrl(path) */
        metaUrl : function(path) {
            return this.config.meta_url.replace("__PATH__", path);
            },

        /* imageUrl(path, size) */
        imageUrl : function(path, size) {
            url = this.config.stream_url.replace("__PATH__", path).
                replace("__SIZE__", size);
            return url;
            },
            
        /* zipUrl(files) */
        zipUrl : function(files) {
            url = this.config.stream_url.replace("__FILES__", files);
            return url;
            },
        
        listDir : function(path, per_page, page) {
            var deffered = $q.defer();
            
            url = this.config.listdir_url.
                replace("__PATH__", path).
                replace("__PERPAGE__", per_page).
                replace("__PAGE__", page);

            $http.get(url).success(function(data) {
                deffered.resolve(data);
                });
                
            return deffered.promise;
            },
            
        zip : function(files) {
            url = this.config.zip_url.
                replace("__FILES__", JSON.stringify(files));
            $window.location.href = url;
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
["$scope", "$http", "$location", "$rootScope", "dirws", 
function($scope, $http, $location, $rootScope, dirws) {
                
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

    $scope.toHash = function() {
        $location.hash(angular.toJson({
            'image': $scope.image,
            'per_page': $scope.per_page,
            'page': $scope.page,
            'path': $scope.path,
            'size': $scope.size,
            'show_exif': $scope.show_exif,
            'selecting': $scope.selecting,
            'use_scroll': $scope.use_scroll
        }));
    };
    
    $scope.fromHash = function() {
        if ($location.hash() == "")
            return false;
        h = angular.fromJson($location.hash());
        $scope.per_page = h['per_page'];
        $scope.page = h['page'];
        $scope.path = h['path'];
        $scope.size = h['size'];
        $scope.image = h['image'];

        $scope.show_exif = h['show_exif'];
        $scope.selecting = h['selecting'];
        $scope.use_scroll = h['use_scroll'];
        return true;
    };
    
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
    $scope.in_basket = false;
    $scope.dirws = dirws;
    $scope.basket = [];
    $scope.displayed_images = [];

    
    $scope.setPath = function (path) { $scope.path = path; };
    $scope.setSize = function (size) { $scope.size = size; };
    $scope.setPage = function (page) { $scope.page = page; };
    $scope.setPerPage = function (per_page) { $scope.per_page = per_page; };
   
    $scope.toggleExif = function () { $scope.show_exif = !$scope.show_exif; };
    $scope.toggleScroll = function () { $scope.use_scroll = !$scope.use_scroll; };
    $scope.toggleSelecting = function () { $scope.selecting = !$scope.selecting; };
    $scope.toggleInBasket = function () { $scope.in_basket = !$scope.in_basket; };
    

    /* set current image or select it, depending on mode */
    $scope.clickImage = function (image) { 
        if (image == "")
            $scope.image = "";   // clear
        else if ($scope.selecting) {
            $scope.putImage(image);  // select mode
        } else
            $scope.image = image;  // set active
    };

    /* put/remove image in/from basket */
    $scope.putImage = function (image) {
        index = $scope.basket.indexOf(image);
        if (index != -1)
            $scope.basket.splice(index, 1);
        else
            $scope.basket.push(image);
    };
    
    
    $scope.inBasket = function (image) {
        index = $scope.basket.indexOf(image);
        return index != -1;
    };


    $scope.zip = function (image) {
        index = $scope.basket.indexOf(image);
        return index != -1;
    };
    

    $scope.$watch("path", function(new_value, old_value) {
        if (new_value !== old_value) {
            //$scope.toHash();
            $scope.in_basket = false;
            refresh();
        }
    });
    
    $scope.$watch("page", function(new_value, old_value) {
        if (new_value !== old_value) {
            //$scope.toHash();
            refresh();
        }
    });

    $scope.$watch("per_page", function(new_value, old_value) {
        if (new_value !== old_value) {
            //$scope.toHash();
            $scope.page = 0;
            refresh();
        }
    });

    $scope.$watch("image", function(new_value, old_value) {
        if (new_value !== old_value && new_value != "") {
            url = dirws.metaUrl(new_value);
            $http.get(url).
                success(function(data, status, headers, config) {
                    $scope.meta = data;
                });
        }
    });
    
    $scope.$watch("in_basket", function(new_value, old_value) {
        if (new_value !== old_value) {

            if (new_value) {  // load basket
                $scope.displayed_images = $scope.basket;
            }
            else if (!new_value) {  // load cached images
                $scope.displayed_images = [];
                angular.forEach($scope.files, function(value, key) {
                    $scope.displayed_images.push($scope.path + '/'+ value['name'])
                    });            
            }
        }
    });

    dirws.setup().then(function(data) {
        $scope.path = '/';  // trigger listDir
        $scope.size = data.sizes[1];
    });
}]);
