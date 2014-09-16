angular.module("dirshareApp").factory(
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
            var url = this.config.zip_url.replace("__FILES__", JSON.stringify(files));
            return url;
            },

        /* rebuildUrl(path) */
        rebuildUrl : function(path) {
            var url = this.config.rebuild_url.replace("__PATH__", path);
            return url;
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

        cleanPath: function(path) {
            var p = path;
            while (1) {
                var n = p.search("//");
                if (n == -1)
                    break;
                p = p.replace("//", "/");
            }

            if (p[p.length-1] != '/')
                p = p + "/";

            return p;
        },

        preloadImage: function(id, url) {
            var deffered = $q.defer();
            var i = $(new Image());

            i.load(
                function(event) {
                    deffered.resolve({'id': id, 'url': url});
                });

            i.error(
                function(event) {
                    deffered.reject();
                });

            // trigger load
            i.prop( "src", url );

            return deffered.promise;
        },

        /* invoke http method */
        zip : function(files) {
            var url = this.zipUrl(files);
            $window.location.href = url;
        },

        /* invoke http method */
        listDir : function(path, per_page, page) {
            var deffered = $q.defer();

            var url = this.config.listdir_url.
                replace("__PATH__", path).
                replace("__PERPAGE__", per_page).
                replace("__PAGE__", page);

            $http.get(url).success(
                function(data) {
                    deffered.resolve(data);
                }
            ).error(
                function() {
                    deffered.reject();
                }
            );

            return deffered.promise;
        },

        /* invoke http method */
        rebuild : function(path) {
            var url = this.rebuildUrl(path);
            var deffered = $q.defer();

            $http.get(url).success(function(data) {
                deffered.resolve(data);
                });

            return deffered.promise;
        },

        /* invoke http method */
        getJobs : function() {
            var url = this.config.getjobs_url;
            var deffered = $q.defer();

            $http.get(url).success(function(data) {
                deffered.resolve(data);
                });

            return deffered.promise;
        },


        /* invoke http method */
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



/*
Images
*/

angular.module("dirshareApp").factory(
'images',
['$http', '$q', '$window', 'dirws', function($http, $q, $window, dirws) {
    var service = {
        _images: {
        },

        contains: function(full_path) {
            return full_path in this._images;
        },

        hasMetadata: function(full_path) {
            return this._images[full_path].metadata.metadata && true;
        },

        getMetadata: function(full_path) {
            return this._images[full_path].metadata.metadata;
        },

        sizeLoaded: function(full_path, size) {
            if (!(full_path in this._images))
                return false;
            if (!(size in this._images[full_path].sizes))
                return false;
            return this._images[full_path].sizes[size].loaded;
        },

        getSizeUrl: function(full_path, size) {
            return this._images[full_path].sizes[size].url;
        },

        hasSize: function(full_path, size) {
            return size in this._images[full_path].sizes;
        },

        getImage: function(full_path) {
            return this._images[full_path];
        },

        save: function(full_path, obj) {
            this._images[full_path] = obj;
        },

        cacheThumbnail: function(full_path, success) {
            this.cacheSized(full_path, dirws.config.thumb_size, success);
        },

        cacheSized: function(full_path, size, success) {
            console.log("cacheSized()", full_path, size);
            if (!(size in service._images[full_path].sizes)) {
                service._images[full_path].sizes[size] = {
                    'url': dirws.imageUrl(full_path, size),
                    'loaded': false
                }
            }

            /* preload image */
            if (!this._images[full_path].sizes[size].loaded) {
                var id = {'id': full_path, 'size': size};
                var url = this._images[full_path].sizes[size]['url'];

                var i = new Image();

                angular.element(i).bind(
                    'load',
                    function(res) {
                        service._images[full_path].sizes[size].loaded = true;
                        console.log("cacheSized() complete", full_path, size);
                        success(service._images[full_path]);
                    }
                );

                angular.element(i).prop("src", url);
            }
        },

        cacheMetadata: function(full_path) {
            console.log("cacheMetadata()", full_path);
            if (!this._images[full_path].metadata.metadata) {
                var url = dirws.metaUrl(full_path);
                var cb = function(data) {
                    console.log("cacheMetadata() complete", full_path);
                    service._images[full_path].metadata = data;
                };
                $http.get(url).success(cb);
            }
        },

        remove: function(full_path) {
            if (contains(full_path))
                delete this._images[full_path];
        },
    };

    return service;
}]);
