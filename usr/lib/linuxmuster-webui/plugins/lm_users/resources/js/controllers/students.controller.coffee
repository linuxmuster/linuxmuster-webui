angular.module('lm.users').config ($routeProvider) ->
    $routeProvider.when '/view/lm/users/students',
        controller: 'LMUsersStudentsController'
        templateUrl: '/lm_users:resources/partial/students.html'


angular.module('lm.users').controller 'LMUsersStudentsController', ($scope, $http, $location, $route, $uibModal, gettext, notify, lmEncodingMap, messagebox, pageTitle, lmFileEditor, lmFileBackups) ->
    pageTitle.set(gettext('Students'))

    $scope.sorts = [
        {
            name: gettext('Class')
            fx: (x) -> x.class
        }
        {
            name: gettext('First name')
            fx: (x) -> x.first_name
        }
        {
            name: gettext('Last name')
            fx: (x) -> x.last_name
        }
        {
            name: gettext('Birthday')
            fx: (x) -> x.birthday
        }
    ]
    $scope.sort = $scope.sorts[0]
    $scope.paging =
        page: 1
        pageSize: 100

    $scope.add = () ->
        $scope.paging.page = Math.floor(($scope.students.length - 1) / $scope.paging.pageSize) + 1
        $scope.filter = ''
        $scope.students.push {first_name: 'New', _isNew: true}

    $http.get('/api/lm/settings').then (resp) ->
        $scope.encoding = lmEncodingMap[resp.data.encoding_students] or 'ISO8859-1'
        $http.get("/api/lm/users/students?encoding=#{$scope.encoding}").then (resp) ->
            $scope.students = resp.data

    $scope.remove = (student) ->
        $scope.students.remove(student)

    $scope.editCSV = () ->
        lmFileEditor.show('/etc/sophomorix/user/schueler.txt', $scope.encoding).then () ->
            $route.reload()

    $scope.save = () ->
        return $http.post("/api/lm/users/students?encoding=#{$scope.encoding}", $scope.students).then () ->
            notify.success gettext('Saved')

    $scope.saveAndCheck = () ->
        $scope.save().then () ->
            $uibModal.open(
                templateUrl: '/lm_users:resources/partial/check.modal.html'
                controller: 'LMUsersCheckModalController'
                backdrop: 'static'
            )

    $scope.backups = () ->
        lmFileBackups.show('/etc/sophomorix/user/schueler.txt', $scope.encoding)
