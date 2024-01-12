local k = import 'github.com/grafana/jsonnet-libs/ksonnet-util/kausal.libsonnet';

{
  config:: {
    sts: {
      name: 'randomactionbot',
      image: std.join(":", [std.extVar("IMAGE_NAME"), std.extVar("IMAGE_TAG")]),
    },
    secret: {
      name: 'random-action-bot',
    },
    configmap: {
      name: 'random-action-bot',
      api: {
        url: 'http://api.timhatdiehandandermaus:8080',
      },
    },
  },

  local configmap = k.core.v1.configMap,
  local sts = k.apps.v1.statefulSet,
  local container = k.core.v1.container,
  local secret = k.core.v1.secret,
  local envFromSource = k.core.v1.envFromSource,

  bot: {
    deployment: sts.new(
      name=$.config.sts.name,
      replicas=1,
      containers=[
        container.new(
          $.config.sts.name,
          $.config.sts.image
        ) + container.withEnvFrom([
          envFromSource.secretRef.withName($.config.secret.name),
          envFromSource.configMapRef.withName($.config.configmap.name),
        ]) + container.withResourcesRequests(
          cpu='50m',
          memory='50Mi'
        ) + container.withResourcesLimits(
          cpu='300m',
          memory='300Mi'
        ) + container.withImagePullPolicy('IfNotPresent'),
      ],
    ),
    secret: secret.new(
      name=$.config.secret.name,
      data={
        BOT_TOKEN: std.extVar('BOT_TOKEN'),
        API_NINJAS_KEY: std.extVar('API_NINJAS_KEY'),
        THE_CATS_API_KEY: std.extVar('THE_CATS_API_KEY'),
        NASA_API_KEY: std.extVar('NASA_API_KEY'),
      }
    ),
    configmap: configmap.new(
      name=$.config.configmap.name,
      data={
        TIM_API_URL: $.config.configmap.api.url,
      },
    )
  },
}
