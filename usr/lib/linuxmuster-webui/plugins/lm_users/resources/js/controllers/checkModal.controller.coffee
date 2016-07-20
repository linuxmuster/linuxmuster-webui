angular.module('lm.users').controller 'LMUsersCheckResultsModalController', ($scope, $uibModalInstance, $uibModal, data) ->
    $scope.data = data
    $scope._ = {
        doAdd: data.add.length > 0
        doMove: data.move.length > 0
        doKill: data.kill.length > 0
    }

    $scope.apply = () ->
        $uibModalInstance.close()
        msg = $uibModal.open(
            templateUrl: '/lm_users:resources/partial/apply.modal.html'
            controller: 'LMUsersApplyModalController'
            backdrop: 'static'
            resolve:
                params: () -> $scope._
        )

        $uibModalInstance.close()

    $scope.cancel = () ->
        $uibModalInstance.dismiss()


angular.module('lm.users').controller 'LMUsersApplyModalController', ($scope, $uibModalInstance, $http, $route, gettext, notify, params) ->
    $scope.close = () ->
        $uibModalInstance.close()

    $scope.isWorking = true
    $http.post('/api/lm/users/apply', params).then (resp) ->
        $scope.isWorking = false
        notify.success gettext('Changes applied')
        $route.reload()
    .catch (resp) ->
        $scope.isWorking = false
        notify.error gettext('Failed'), resp.data.message


angular.module('lm.users').controller 'LMUsersCheckModalController', ($scope, $http, notify, $uibModalInstance, $uibModal, gettext) ->
    $scope.isWorking = true

    $http.get('/api/lm/users/check').then (resp) ->
        $scope.showCheckResults(resp.data)
        $uibModalInstance.close()
    .catch (resp) ->
        $scope.isWorking = false
        $scope.error = true
        notify.error gettext('Check failed'), resp.data.message

    $scope.showCheckResults = (data) ->
        $uibModal.open(
            templateUrl: '/lm_users:resources/partial/result.modal.html'
            controller: 'LMUsersCheckResultsModalController'
            resolve:
                data: () -> data
        )

    $scope.close = () ->
        $uibModalInstance.close()
