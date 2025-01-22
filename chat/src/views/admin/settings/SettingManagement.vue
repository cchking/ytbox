<template>
  <div class="container mx-auto p-4 md:p-6 bg-white">
    <h1 class="text-xl md:text-2xl font-bold mb-4 md:mb-6">系统设置</h1>

    <!-- 成功提示 -->
    <div
      v-if="showSuccess"
      class="mb-4 p-3 md:p-4 rounded-lg bg-green-50 text-green-700"
    >
      <p>设置已保存成功！</p>
    </div>

    <!-- 移动端选项卡下拉菜单 -->
    <div class="md:hidden mb-4">
      <select
        v-model="activeTab"
        class="w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
      >
        <option v-for="tab in tabs" :key="tab.value" :value="tab.value">
          {{ tab.label }}
        </option>
      </select>
    </div>

    <!-- 桌面端选项卡 -->
    <div class="hidden md:flex space-x-2 border-b mb-6">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        @click="activeTab = tab.value"
        class="flex items-center gap-2 px-4 py-2 -mb-px"
        :class="[
          activeTab === tab.value
            ? 'border-b-2 border-black text-black font-medium'
            : 'text-gray-500 hover:text-gray-700',
        ]"
      >
        <component :is="tab.icon" class="h-4 w-4" />
        {{ tab.label }}
      </button>
    </div>

    <!-- 使用限制 -->
    <div v-show="activeTab === 'limits'" class="space-y-4 md:space-y-6">
      <!-- 普通用户限制 -->
      <div class="rounded-lg border shadow-sm">
        <div class="flex flex-col space-y-1.5 p-4 md:p-6 border-b">
          <h3 class="text-base md:text-lg font-semibold">普通用户使用限制</h3>
        </div>
        <div class="p-4 md:p-6 space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-2">
              <label class="text-sm font-medium">每分钟请求数 (RPM)</label>
              <input
                type="number"
                v-model="settings.rpmLimit"
                min="0"
                class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
              />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium">每分钟Token数 (RTM)</label>
              <input
                type="number"
                v-model="settings.rtmLimit"
                min="0"
                class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
              />
            </div>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium">每日请求限制</label>
            <input
              type="number"
              v-model="settings.dailyLimit"
              min="0"
              class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
            />
          </div>
        </div>
      </div>

      <!-- VIP用户限制 -->
      <div class="rounded-lg border shadow-sm">
        <div class="flex flex-col space-y-1.5 p-4 md:p-6 border-b">
          <h3 class="text-base md:text-lg font-semibold">VIP用户使用限制</h3>
        </div>
        <div class="p-4 md:p-6 space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-2">
              <label class="text-sm font-medium">每分钟请求数 (RPM)</label>
              <input
                type="number"
                v-model="settings.vipRpmLimit"
                min="0"
                class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
              />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium">每分钟Token数 (RTM)</label>
              <input
                type="number"
                v-model="settings.vipRtmLimit"
                min="0"
                class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
              />
            </div>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium">每日请求限制</label>
            <input
              type="number"
              v-model="settings.vipDailyLimit"
              min="0"
              class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 违禁词管理 -->
    <div v-show="activeTab === 'forbidden'" class="space-y-4 md:space-y-6">
      <div class="rounded-lg border shadow-sm">
        <div class="flex flex-col space-y-1.5 p-4 md:p-6 border-b">
          <h3 class="text-base md:text-lg font-semibold">违禁词管理</h3>
        </div>
        <div class="p-4 md:p-6 space-y-6">
          <!-- 添加违禁词表单 -->
          <div class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="space-y-2">
                <label class="text-sm font-medium">违禁词</label>
                <input
                  v-model="newWord.word"
                  type="text"
                  placeholder="输入违禁词"
                  class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
                />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium">级别</label>
                <select
                  v-model="newWord.level"
                  class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
                >
                  <option value="low">低</option>
                  <option value="medium">中</option>
                  <option value="high">高</option>
                </select>
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium">描述</label>
                <input
                  v-model="newWord.description"
                  type="text"
                  placeholder="描述（可选）"
                  class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
                />
              </div>
            </div>
            <button
              @click="addForbiddenWord"
              class="w-full md:w-auto inline-flex items-center justify-center rounded-md text-sm font-medium bg-black text-white hover:bg-black/90 h-10 px-4 py-2"
            >
              添加违禁词
            </button>
          </div>

          <!-- 违禁词列表 -->
          <div class="mt-6">
            <!-- 移动端卡片布局 -->
            <div class="md:hidden space-y-4">
              <div
                v-for="word in forbiddenWords"
                :key="word.id"
                class="border rounded-lg p-4 space-y-3"
              >
                <div class="flex justify-between items-center">
                  <span class="font-medium">{{ word.word }}</span>
                  <span
                    class="text-sm px-2 py-1 rounded-full"
                    :class="{
                      'bg-yellow-50 text-yellow-700': word.level === 'low',
                      'bg-orange-50 text-orange-700': word.level === 'medium',
                      'bg-red-50 text-red-700': word.level === 'high',
                    }"
                  >
                    {{
                      word.level === "low"
                        ? "低"
                        : word.level === "medium"
                        ? "中"
                        : "高"
                    }}
                  </span>
                </div>
                <p class="text-sm text-gray-600">{{ word.description }}</p>
                <div class="flex justify-end">
                  <button
                    @click="deleteForbiddenWord(word.id)"
                    class="text-red-600 hover:text-red-800 text-sm"
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>

            <!-- 桌面端表格布局 -->
            <table class="hidden md:table w-full border-collapse">
              <thead>
                <tr class="border-b">
                  <th class="text-left py-2">违禁词</th>
                  <th class="text-left py-2">级别</th>
                  <th class="text-left py-2">描述</th>
                  <th class="text-left py-2">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="word in forbiddenWords"
                  :key="word.id"
                  class="border-b"
                >
                  <td class="py-2">{{ word.word }}</td>
                  <td class="py-2">
                    {{
                      word.level === "low"
                        ? "低"
                        : word.level === "medium"
                        ? "中"
                        : "高"
                    }}
                  </td>
                  <td class="py-2">{{ word.description }}</td>
                  <td class="py-2">
                    <button
                      @click="deleteForbiddenWord(word.id)"
                      class="text-red-600 hover:text-red-800"
                    >
                      删除
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 邮件设置 -->
    <div v-show="activeTab === 'smtp'" class="space-y-4 md:space-y-6">
      <div class="rounded-lg border shadow-sm">
        <div class="flex flex-col space-y-1.5 p-4 md:p-6 border-b">
          <h3 class="text-base md:text-lg font-semibold">SMTP 邮件配置</h3>
        </div>
        <div class="p-4 md:p-6 space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="space-y-2">
              <label class="text-sm font-medium">SMTP 服务器</label>
              <input
                type="text"
                v-model="settings.smtp.host"
                placeholder="smtp.example.com"
                class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
              />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium">SMTP 端口</label>
              <input
                type="number"
                v-model="settings.smtp.port"
                placeholder="587"
                class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
              />
            </div>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium">SMTP 用户名</label>
            <input
              type="text"
              v-model="settings.smtp.user"
              placeholder="username@example.com"
              class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
            />
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium">SMTP 密码</label>
            <input
              type="password"
              v-model="settings.smtp.pass"
              placeholder="输入密码"
              class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
            />
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium">发件人地址</label>
            <input
              type="email"
              v-model="settings.smtp.from"
              placeholder="noreply@example.com"
              class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
            />
          </div>
          <button
            @click="testSmtp"
            :disabled="testingSmtp"
            class="w-full md:w-auto inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-white transition-colors border border-gray-200 bg-white hover:bg-gray-100 h-10 px-4 py-2"
          >
            {{ testingSmtp ? "测试中..." : "测试邮件配置" }}
          </button>
        </div>
      </div>
    </div>

    <!-- 系统设置 -->
    <div v-show="activeTab === 'system'" class="space-y-4 md:space-y-6">
      <!-- 签到设置 -->
      <div class="rounded-lg border shadow-sm">
        <div class="flex flex-col space-y-1.5 p-4 md:p-6 border-b">
          <h3 class="text-base md:text-lg font-semibold">签到设置</h3>
        </div>
        <div class="p-4 md:p-6 space-y-6">
          <!-- 签到功能开关 -->
          <div class="flex items-center justify-between">
            <div class="space-y-0.5 flex-1">
              <label class="text-sm font-medium">启用每日签到</label>
              <div class="text-xs text-gray-500">
                允许用户进行每日签到获取奖励
              </div>
            </div>
            <button
              type="button"
              role="switch"
              :aria-checked="settings.signin_enabled"
              @click="settings.signin_enabled = !settings.signin_enabled"
              class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-950 focus-visible:ring-offset-2"
              :class="[settings.signin_enabled ? 'bg-black' : 'bg-gray-200']"
            >
              <span
                class="inline-block h-5 w-5 transform rounded-full bg-white transition-transform shadow-sm"
                :class="[
                  settings.signin_enabled ? 'translate-x-6' : 'translate-x-0.5',
                ]"
              />
            </button>
          </div>

          <!-- 签到奖励设置 -->
          <div
            class="grid grid-cols-1 md:grid-cols-2 gap-4"
            :class="{ 'opacity-50': !settings.signin_enabled }"
          >
            <div class="space-y-2">
              <label class="text-sm font-medium">奖励类型</label>
              <select
                v-model="settings.signin_reward_type"
                :disabled="!settings.signin_enabled"
                class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
              >
                <option value="coin">金币</option>
                <option value="vip">VIP天数</option>
              </select>
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium">
                {{
                  settings.signin_reward_type === "coin"
                    ? "金币数量"
                    : "VIP天数"
                }}
              </label>
              <input
                type="number"
                v-model="settings.signin_reward_amount"
                :disabled="!settings.signin_enabled"
                min="1"
                :placeholder="
                  settings.signin_reward_type === 'coin'
                    ? '每日签到金币数'
                    : '每日签到获得的VIP天数'
                "
                class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 邀请奖励设置 -->
      <div class="rounded-lg border shadow-sm">
        <div class="flex flex-col space-y-1.5 p-4 md:p-6 border-b">
          <h3 class="text-base md:text-lg font-semibold">邀请奖励设置</h3>
        </div>
        <div class="p-4 md:p-6 space-y-6">
          <!-- 邀请功能开关 -->
          <div class="flex items-center justify-between">
            <div class="space-y-0.5 flex-1">
              <label class="text-sm font-medium">启用邀请功能</label>
              <div class="text-xs text-gray-500">
                允许用户通过邀请码邀请新用户注册
              </div>
            </div>
            <button
              type="button"
              role="switch"
              :aria-checked="settings.invite_enabled"
              @click="settings.invite_enabled = !settings.invite_enabled"
              class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-950 focus-visible:ring-offset-2"
              :class="[settings.invite_enabled ? 'bg-black' : 'bg-gray-200']"
            >
              <span
                class="inline-block h-5 w-5 transform rounded-full bg-white transition-transform shadow-sm"
                :class="[
                  settings.invite_enabled ? 'translate-x-6' : 'translate-x-0.5',
                ]"
              />
            </button>
          </div>

          <!-- 邀请人奖励设置 -->
          <div
            class="space-y-4"
            :class="{ 'opacity-50': !settings.invite_enabled }"
          >
            <h4 class="font-medium">邀请人奖励</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-2">
                <label class="text-sm font-medium">奖励类型</label>
                <select
                  v-model="settings.inviter_reward_type"
                  :disabled="!settings.invite_enabled"
                  class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
                >
                  <option value="coin">金币</option>
                  <option value="vip">VIP天数</option>
                </select>
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium">奖励数量</label>
                <input
                  type="number"
                  v-model="settings.inviter_reward_amount"
                  :disabled="!settings.invite_enabled"
                  min="1"
                  class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
                />
              </div>
            </div>
          </div>

          <!-- 被邀请人奖励设置 -->
          <div
            class="space-y-4"
            :class="{ 'opacity-50': !settings.invite_enabled }"
          >
            <h4 class="font-medium">被邀请人奖励</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-2">
                <label class="text-sm font-medium">奖励类型</label>
                <select
                  v-model="settings.invitee_reward_type"
                  :disabled="!settings.invite_enabled"
                  class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
                >
                  <option value="coin">金币</option>
                  <option value="vip">VIP天数</option>
                </select>
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium">奖励数量</label>
                <input
                  type="number"
                  v-model="settings.invitee_reward_amount"
                  :disabled="!settings.invite_enabled"
                  min="1"
                  class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- 健康检查设置 -->
      <div class="rounded-lg border shadow-sm">
        <div class="flex flex-col space-y-1.5 p-4 md:p-6 border-b">
          <h3 class="text-base md:text-lg font-semibold">健康检查设置</h3>
        </div>
        <div class="p-4 md:p-6 space-y-6">
          <!-- 健康检查功能开关 -->
          <div class="flex items-center justify-between">
            <div class="space-y-0.5 flex-1">
              <label class="text-sm font-medium">启用健康检查</label>
              <div class="text-xs text-gray-500">
                定期检查所有模型的可用性和响应状态
              </div>
            </div>
            <button
              type="button"
              role="switch"
              :aria-checked="settings.enable_health_check"
              @click="
                settings.enable_health_check = !settings.enable_health_check
              "
              class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-950 focus-visible:ring-offset-2"
              :class="[
                settings.enable_health_check ? 'bg-black' : 'bg-gray-200',
              ]"
            >
              <span
                class="inline-block h-5 w-5 transform rounded-full bg-white transition-transform shadow-sm"
                :class="[
                  settings.enable_health_check
                    ? 'translate-x-6'
                    : 'translate-x-0.5',
                ]"
              />
            </button>
          </div>

          <!-- 健康检查配置 -->
          <div
            class="space-y-4"
            :class="{ 'opacity-50': !settings.enable_health_check }"
          >
            <h4 class="font-medium">检查配置</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-2">
                <label class="text-sm font-medium">检查间隔（分钟）</label>
                <input
                  type="number"
                  v-model="settings.health_check_interval"
                  :disabled="!settings.enable_health_check"
                  min="1"
                  placeholder="建议间隔：5分钟"
                  class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
                />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium">批量检查数量</label>
                <input
                  type="number"
                  v-model="settings.health_check_batch_size"
                  :disabled="!settings.enable_health_check"
                  min="1"
                  placeholder="建议数量：500"
                  class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
                />
              </div>
            </div>
            <div class="text-xs text-gray-500">
              <p>建议检查间隔：5分钟或以上，间隔越短系统资源消耗越大</p>
              <p>建议批量数量：根据实际模型数量调整，默认500个</p>
            </div>
          </div>
        </div>
      </div>
      <!-- 基本系统设置 -->
      <div class="rounded-lg border shadow-sm">
        <div class="flex flex-col space-y-1.5 p-4 md:p-6 border-b">
          <h3 class="text-base md:text-lg font-semibold">系统配置</h3>
        </div>
        <div class="p-4 md:p-6 space-y-6">
          <!-- 系统开关设置 -->
          <div class="space-y-6">
            <div class="flex items-center justify-between">
              <div class="space-y-0.5 flex-1">
                <label class="text-sm font-medium">允许新用户注册</label>
                <div class="text-xs text-gray-500">
                  启用后新用户可以自行注册账号
                </div>
              </div>
              <button
                type="button"
                role="switch"
                :aria-checked="settings.allowRegistration"
                @click="
                  settings.allowRegistration = !settings.allowRegistration
                "
                class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-950 focus-visible:ring-offset-2"
                :class="[
                  settings.allowRegistration ? 'bg-black' : 'bg-gray-200',
                ]"
              >
                <span
                  class="inline-block h-5 w-5 transform rounded-full bg-white transition-transform shadow-sm"
                  :class="[
                    settings.allowRegistration
                      ? 'translate-x-6'
                      : 'translate-x-0.5',
                  ]"
                />
              </button>
            </div>

            <div class="flex items-center justify-between">
              <div class="space-y-0.5 flex-1">
                <label class="text-sm font-medium">要求邮箱验证</label>
                <div class="text-xs text-gray-500">
                  新用户注册后需要验证邮箱才能使用系统
                </div>
              </div>
              <button
                type="button"
                role="switch"
                :aria-checked="settings.requireEmailVerification"
                @click="
                  settings.requireEmailVerification =
                    !settings.requireEmailVerification
                "
                class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-950 focus-visible:ring-offset-2"
                :class="[
                  settings.requireEmailVerification
                    ? 'bg-black'
                    : 'bg-gray-200',
                ]"
              >
                <span
                  class="inline-block h-5 w-5 transform rounded-full bg-white transition-transform shadow-sm"
                  :class="[
                    settings.requireEmailVerification
                      ? 'translate-x-6'
                      : 'translate-x-0.5',
                  ]"
                />
              </button>
            </div>

            <div class="flex items-center justify-between">
              <div class="space-y-0.5 flex-1">
                <label class="text-sm font-medium">允许用户登录</label>
                <div class="text-xs text-gray-500">
                  关闭后所有非管理员用户将无法登录系统
                </div>
              </div>
              <button
                type="button"
                role="switch"
                :aria-checked="settings.allowLogin"
                @click="settings.allowLogin = !settings.allowLogin"
                class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-950 focus-visible:ring-offset-2"
                :class="[settings.allowLogin ? 'bg-black' : 'bg-gray-200']"
              >
                <span
                  class="inline-block h-5 w-5 transform rounded-full bg-white transition-transform shadow-sm"
                  :class="[
                    settings.allowLogin ? 'translate-x-6' : 'translate-x-0.5',
                  ]"
                />
              </button>
            </div>

            <div class="flex items-center justify-between">
              <div class="space-y-0.5 flex-1">
                <label class="text-sm font-medium">启用系统日志</label>
                <div class="text-xs text-gray-500">
                  记录系统API请求和响应的详细日志
                </div>
              </div>
              <button
                type="button"
                role="switch"
                :aria-checked="settings.enableSystemLogs"
                @click="settings.enableSystemLogs = !settings.enableSystemLogs"
                class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-950 focus-visible:ring-offset-2"
                :class="[
                  settings.enableSystemLogs ? 'bg-black' : 'bg-gray-200',
                ]"
              >
                <span
                  class="inline-block h-5 w-5 transform rounded-full bg-white transition-transform shadow-sm"
                  :class="[
                    settings.enableSystemLogs
                      ? 'translate-x-6'
                      : 'translate-x-0.5',
                  ]"
                />
              </button>
            </div>

            <div class="flex items-center justify-between">
              <div class="space-y-0.5 flex-1">
                <label class="text-sm font-medium">启用违禁词检测</label>
                <div class="text-xs text-gray-500">
                  开启后系统将自动检测和阻止包含违禁词的对话
                </div>
              </div>
              <button
                type="button"
                role="switch"
                :aria-checked="settings.enableForbiddenWords"
                @click="
                  settings.enableForbiddenWords = !settings.enableForbiddenWords
                "
                class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-950 focus-visible:ring-offset-2"
                :class="[
                  settings.enableForbiddenWords ? 'bg-black' : 'bg-gray-200',
                ]"
              >
                <span
                  class="inline-block h-5 w-5 transform rounded-full bg-white transition-transform shadow-sm"
                  :class="[
                    settings.enableForbiddenWords
                      ? 'translate-x-6'
                      : 'translate-x-0.5',
                  ]"
                />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 邮箱白名单管理 -->
      <div class="rounded-lg border shadow-sm mt-6">
        <div class="flex flex-col space-y-1.5 p-4 md:p-6 border-b">
          <h3 class="text-base md:text-lg font-semibold">邮箱白名单管理</h3>
        </div>
        <div class="p-4 md:p-6 space-y-6">
          <!-- 白名单功能开关 -->
          <div class="flex items-center justify-between">
            <div class="space-y-0.5 flex-1">
              <label class="text-sm font-medium">启用邮箱白名单</label>
              <div class="text-xs text-gray-500">
                开启后只有白名单内的邮箱域名才能注册
              </div>
            </div>
            <button
              type="button"
              role="switch"
              :aria-checked="settings.enable_email_whitelist"
              @click="
                settings.enable_email_whitelist =
                  !settings.enable_email_whitelist
              "
              class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-950 focus-visible:ring-offset-2"
              :class="[
                settings.enable_email_whitelist ? 'bg-black' : 'bg-gray-200',
              ]"
            >
              <span
                class="inline-block h-5 w-5 transform rounded-full bg-white transition-transform shadow-sm"
                :class="[
                  settings.enable_email_whitelist
                    ? 'translate-x-6'
                    : 'translate-x-0.5',
                ]"
              />
            </button>
          </div>

          <!-- 添加白名单规则表单 -->
          <div
            class="space-y-4"
            :class="{ 'opacity-50': !settings.enable_email_whitelist }"
          >
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-2">
                <label class="text-sm font-medium">邮箱域名</label>
                <input
                  v-model="newWhitelistRule.pattern"
                  type="text"
                  placeholder="输入域名，如 @example.com"
                  :disabled="!settings.enable_email_whitelist"
                  class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
                />
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium">描述</label>
                <input
                  v-model="newWhitelistRule.description"
                  type="text"
                  placeholder="规则描述（可选）"
                  :disabled="!settings.enable_email_whitelist"
                  class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
                />
              </div>
            </div>
            <button
              @click="addWhitelistRule"
              :disabled="!settings.enable_email_whitelist"
              class="w-full md:w-auto inline-flex items-center justify-center rounded-md text-sm font-medium bg-black text-white hover:bg-black/90 h-10 px-4 py-2"
            >
              添加规则
            </button>
          </div>

          <!-- 白名单规则列表 -->
          <div
            class="mt-6"
            :class="{ 'opacity-50': !settings.enable_email_whitelist }"
          >
            <!-- 移动端卡片布局 -->
            <div class="md:hidden space-y-4">
              <div
                v-for="rule in whitelistRules"
                :key="rule.id"
                class="border rounded-lg p-4 space-y-3"
              >
                <div class="flex justify-between items-center">
                  <span class="font-medium">{{ rule.pattern }}</span>
                  <span
                    :class="rule.is_active ? 'text-green-600' : 'text-gray-500'"
                  >
                    {{ rule.is_active ? "启用" : "禁用" }}
                  </span>
                </div>
                <p class="text-sm text-gray-600">{{ rule.description }}</p>
                <div class="flex justify-end gap-4">
                  <button
                    @click="toggleWhitelistRule(rule)"
                    class="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    {{ rule.is_active ? "禁用" : "启用" }}
                  </button>
                  <button
                    @click="deleteWhitelistRule(rule.id)"
                    class="text-red-600 hover:text-red-800 text-sm"
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>

            <!-- 桌面端表格布局 -->
            <table class="hidden md:table w-full border-collapse">
              <thead>
                <tr class="border-b">
                  <th class="text-left py-2">域名</th>
                  <th class="text-left py-2">描述</th>
                  <th class="text-left py-2">状态</th>
                  <th class="text-left py-2">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="rule in whitelistRules"
                  :key="rule.id"
                  class="border-b"
                >
                  <td class="py-2">{{ rule.pattern }}</td>
                  <td class="py-2">{{ rule.description }}</td>
                  <td class="py-2">
                    <span
                      :class="
                        rule.is_active ? 'text-green-600' : 'text-gray-500'
                      "
                    >
                      {{ rule.is_active ? "启用" : "禁用" }}
                    </span>
                  </td>
                  <td class="py-2">
                    <div class="flex gap-2">
                      <button
                        @click="toggleWhitelistRule(rule)"
                        class="text-blue-600 hover:text-blue-800"
                      >
                        {{ rule.is_active ? "禁用" : "启用" }}
                      </button>
                      <button
                        @click="deleteWhitelistRule(rule.id)"
                        class="text-red-600 hover:text-red-800"
                      >
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 前端设置 tab 内容 -->
    <div v-show="activeTab === 'frontend'" class="space-y-4 md:space-y-6">
      <div class="rounded-lg border shadow-sm">
        <div class="flex flex-col space-y-1.5 p-4 md:p-6 border-b">
          <h3 class="text-base md:text-lg font-semibold">前端设置</h3>
        </div>
        <div class="p-4 md:p-6 space-y-4">
          <!-- Logo 上传 -->
          <div class="space-y-2">
            <label class="text-sm font-medium">网站 Logo</label>
            <div class="flex flex-wrap md:flex-nowrap items-center gap-4">
              <img
                v-if="settings.frontend_logo"
                :src="settings.frontend_logo"
                alt="网站Logo"
                class="h-10 w-auto"
              />
              <input
                type="file"
                ref="logoInput"
                @change="handleLogoUpload"
                accept="image/*"
                class="hidden"
              />
              <button
                @click="$refs.logoInput.click()"
                class="w-full md:w-auto inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-white transition-colors border border-gray-200 bg-white hover:bg-gray-100 h-10 px-4 py-2"
              >
                {{ settings.frontend_logo ? "更换Logo" : "上传Logo" }}
              </button>
              <button
                v-if="settings.frontend_logo"
                @click="settings.frontend_logo = ''"
                class="w-full md:w-auto text-red-600 hover:text-red-800"
              >
                删除
              </button>
            </div>
          </div>

          <!-- 网站标题 -->
          <div class="space-y-2">
            <label class="text-sm font-medium">网站标题</label>
            <input
              v-model="settings.frontend_title"
              type="text"
              placeholder="请输入网站标题"
              class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
            />
          </div>
          <!-- 卡密购买设置 -->
          <div class="rounded-lg border shadow-sm">
            <div class="flex flex-col space-y-1.5 p-4 md:p-6 border-b">
              <h3 class="text-base md:text-lg font-semibold">卡密购买设置</h3>
            </div>
            <div class="p-4 md:p-6 space-y-4">
              <!-- 购买链接输入 -->
              <div class="space-y-2">
                <label class="text-sm font-medium">购买链接</label>
                <input
                  v-model="settings.card_purchase_url"
                  type="text"
                  placeholder="请输入卡密购买链接"
                  class="flex h-10 w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
                />
              </div>

              <!-- 购买说明输入 -->
              <div class="space-y-2">
                <label class="text-sm font-medium">购买说明</label>
                <textarea
                  v-model="settings.card_purchase_description"
                  rows="4"
                  placeholder="请输入卡密购买说明"
                  class="w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm"
                ></textarea>
              </div>
            </div>
          </div>
          <!-- VIP 权益说明 -->
          <div class="space-y-2">
            <label class="text-sm font-medium">VIP权益说明</label>
            <div class="border rounded-md">
              <div
                class="border-b p-2 bg-gray-50 flex flex-wrap md:flex-nowrap justify-between items-center gap-2"
              >
                <div class="flex items-center space-x-4">
                  <span class="text-sm">
                    {{ benefitsMode === "markdown" ? "Markdown" : "HTML" }}
                    编辑器
                  </span>
                  <select
                    v-model="benefitsMode"
                    class="text-sm border rounded px-2 py-1"
                  >
                    <option value="markdown">Markdown</option>
                    <option value="html">HTML</option>
                  </select>
                </div>
                <div>
                  <button
                    @click="previewBenefits = !previewBenefits"
                    class="text-sm text-gray-600 hover:text-gray-900"
                  >
                    {{ previewBenefits ? "编辑" : "预览" }}
                  </button>
                </div>
              </div>
              <template v-if="previewBenefits">
                <div
                  class="p-4 prose max-w-none preview-content"
                  v-html="
                    renderPreview(settings.frontend_vip_benefits, benefitsMode)
                  "
                />
              </template>
              <template v-else>
                <textarea
                  v-model="settings.frontend_vip_benefits"
                  rows="10"
                  :placeholder="
                    benefitsMode === 'markdown'
                      ? '输入Markdown格式的VIP权益说明...'
                      : '输入HTML格式的VIP权益说明...'
                  "
                  class="w-full p-4 text-sm font-mono"
                ></textarea>
              </template>
            </div>
          </div>

          <!-- 使用指南 -->
          <div class="space-y-2">
            <label class="text-sm font-medium">使用指南</label>
            <div class="border rounded-md">
              <div
                class="border-b p-2 bg-gray-50 flex flex-wrap md:flex-nowrap justify-between items-center gap-2"
              >
                <div class="flex items-center space-x-4">
                  <span class="text-sm">
                    {{ guideMode === "markdown" ? "Markdown" : "HTML" }} 编辑器
                  </span>
                  <select
                    v-model="guideMode"
                    class="text-sm border rounded px-2 py-1"
                  >
                    <option value="markdown">Markdown</option>
                    <option value="html">HTML</option>
                  </select>
                </div>
                <div>
                  <button
                    @click="previewGuide = !previewGuide"
                    class="text-sm text-gray-600 hover:text-gray-900"
                  >
                    {{ previewGuide ? "编辑" : "预览" }}
                  </button>
                </div>
              </div>
              <template v-if="previewGuide">
                <div
                  class="p-4 prose max-w-none preview-content"
                  v-html="
                    renderPreview(settings.frontend_user_guide, guideMode)
                  "
                />
              </template>
              <template v-else>
                <textarea
                  v-model="settings.frontend_user_guide"
                  rows="10"
                  :placeholder="
                    guideMode === 'markdown'
                      ? '输入Markdown格式的使用指南...'
                      : '输入HTML格式的使用指南...'
                  "
                  class="w-full p-4 text-sm font-mono"
                ></textarea>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div
      class="fixed md:relative bottom-0 bg-white border-t md:border-t-0 p-4 md:p-0 mt-6 flex justify-end gap-4"
      :style="{
        left: isSidebarOpen ? '256px' : '68px',
        width: isSidebarOpen ? 'calc(100% - 256px)' : 'calc(100% - 68px)',
      }"
    >
      <button
        @click="loadSettings"
        class="flex-1 md:flex-none inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-white transition-colors border border-gray-200 bg-white hover:bg-gray-100 h-10 px-4 py-2"
      >
        重置
      </button>
      <button
        @click="saveSettings"
        :disabled="saving"
        class="flex-1 md:flex-none inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-white transition-colors bg-black text-white hover:bg-black/90 h-10 px-4 py-2"
      >
        {{ saving ? "保存中..." : "保存设置" }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { request } from "@/utils/request";
import { Shield, Mail, Settings, AlertTriangle, LogOut } from "lucide-vue-next";
import { ElMessage } from "element-plus";
import { marked } from "marked";
import DOMPurify from "dompurify";

// 配置 marked 选项
marked.setOptions({
  headerIds: false, // 禁用自动生成的header id
  mangle: false, // 禁用自动生成的header id
  gfm: true, // GitHub风格Markdown
  breaks: true, // 换行符转换为<br>
});

const tabs = [
  { value: "limits", label: "使用限制", icon: Shield },
  { value: "forbidden", label: "违禁词管理", icon: AlertTriangle },
  { value: "smtp", label: "邮件设置", icon: Mail },
  { value: "system", label: "系统设置", icon: Settings },
  { value: "frontend", label: "前端设置", icon: Settings },
];

// 首先定义 settings
const settings = reactive({
  // 使用限制设置
  rpmLimit: 60,
  rtmLimit: 1000,
  dailyLimit: 1000,
  vipRpmLimit: 120,
  vipRtmLimit: 2000,
  vipDailyLimit: 2000,

  // 系统设置
  allowRegistration: true,
  requireEmailVerification: true,
  allowLogin: true,
  enableSystemLogs: true,
  enableForbiddenWords: true,

  // SMTP设置
  smtp: {
    host: "",
    port: 587,
    user: "",
    pass: "",
    from: "",
  },

  // 签到设置
  signin_enabled: true,
  signin_reward_type: "coin",
  signin_reward_amount: 10,

  // 邀请设置
  invite_enabled: true,
  inviter_reward_type: "coin",
  inviter_reward_amount: 100,
  invitee_reward_type: "coin",
  invitee_reward_amount: 50,

  // 前端设置
  frontend_logo: "",
  frontend_title: "",
  frontend_vip_benefits: "",
  frontend_user_guide: "",
  enable_email_whitelist: true,

  // 添加健康检查设置
  enable_health_check: true,
  health_check_interval: 5,
  health_check_batch_size: 500,
});

const activeTab = ref("limits");
const saving = ref(false);
const testingSmtp = ref(false);
const showSuccess = ref(false);
const forbiddenWords = ref([]);
const previewBenefits = ref(false);
const previewGuide = ref(false);
const benefitsMode = ref("markdown"); // 'markdown' 或 'html'
const guideMode = ref("markdown"); // 'markdown' 或 'html'
// 添加响应式状态
const whitelistRules = ref([]);
const newWhitelistRule = reactive({
  pattern: "",
  description: "",
  is_active: true,
});

// 在 settings 对象中添加白名单启用开关
settings.enable_email_whitelist = false;

// 渲染预览的安全函数
const renderPreview = (content, mode = "markdown") => {
  if (!content) return "";
  try {
    if (mode === "markdown") {
      return DOMPurify.sanitize(marked(content), {
        ALLOWED_TAGS: [
          "h1",
          "h2",
          "h3",
          "h4",
          "h5",
          "h6",
          "p",
          "br",
          "b",
          "i",
          "strong",
          "em",
          "ul",
          "ol",
          "li",
          "blockquote",
          "code",
          "pre",
          "a",
          "img",
          "div",
          "span",
        ],
        ALLOWED_ATTR: [
          "href",
          "target",
          "rel",
          "src",
          "alt",
          "title",
          "class",
          "style",
        ],
        ALLOW_DATA_ATTR: false,
        ADD_ATTR: [
          ["target", "_blank"],
          ["rel", "noopener noreferrer"],
        ],
      });
    } else {
      // HTML 模式直接清理 HTML
      return DOMPurify.sanitize(content, {
        ALLOWED_TAGS: [
          "h1",
          "h2",
          "h3",
          "h4",
          "h5",
          "h6",
          "p",
          "br",
          "b",
          "i",
          "strong",
          "em",
          "ul",
          "ol",
          "li",
          "blockquote",
          "code",
          "pre",
          "a",
          "img",
          "div",
          "span",
        ],
        ALLOWED_ATTR: [
          "href",
          "target",
          "rel",
          "src",
          "alt",
          "title",
          "class",
          "style",
        ],
        ALLOW_DATA_ATTR: false,
        ADD_ATTR: [
          ["target", "_blank"],
          ["rel", "noopener noreferrer"],
        ],
      });
    }
  } catch (error) {
    console.error("Preview rendering error:", error);
    return "预览错误";
  }
};

// 内容验证函数
const validateContent = (content) => {
  const suspiciousPatterns = [
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
    /javascript:/gi,
    /onerror=/gi,
    /onload=/gi,
    /onclick=/gi,
    /data:/gi,
  ];
  return !suspiciousPatterns.some((pattern) => pattern.test(content));
};

const newWord = reactive({
  word: "",
  level: "medium",
  description: "",
});

// 添加 Logo 上传处理方法
const handleLogoUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await request("/api/admin/frontend-settings/logo", {
      method: "POST",
      body: formData,
    });
    settings.frontend_logo = response.logo_url;
    ElMessage.success({
      message: "Logo上传成功",
      plain: true,
    });
  } catch (error) {
    console.error("Logo上传失败:", error);
    ElMessage.error({
      message: "Logo上传失败",
      plain: true,
    });
  } finally {
    event.target.value = "";
  }
};

// 获取白名单规则列表
const loadWhitelistRules = async () => {
  try {
    const data = await request("/api/admin/email-whitelist/rules");
    whitelistRules.value = data;
  } catch (error) {
    ElMessage.error({
      message: "加载白名单规则失败",
      plain: true,
    });
  }
};

// 添加白名单规则
const addWhitelistRule = async () => {
  if (!newWhitelistRule.pattern) {
    ElMessage.warning({
      message: "请输入域名",
      plain: true,
    });
    return;
  }

  try {
    await request("/api/admin/email-whitelist/rules", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newWhitelistRule),
    });

    ElMessage.success({
      message: "添加成功",
      plain: true,
    });
    newWhitelistRule.pattern = "";
    newWhitelistRule.description = "";
    await loadWhitelistRules();
  } catch (error) {
    ElMessage.error({
      message: "添加失败",
      plain: true,
    });
  }
};

// 删除白名单规则
const deleteWhitelistRule = async (ruleId) => {
  try {
    await request(`/api/admin/email-whitelist/rules/${ruleId}`, {
      method: "DELETE",
    });
    ElMessage.success({
      message: "删除成功",
      plain: true,
    });
    await loadWhitelistRules();
  } catch (error) {
    ElMessage.error({
      message: "删除失败",
      plain: true,
    });
  }
};

// 切换规则状态
const toggleWhitelistRule = async (rule) => {
  try {
    await request(`/api/admin/email-whitelist/rules/${rule.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...rule,
        is_active: !rule.is_active,
      }),
    });
    ElMessage.success({
      message: "操作成功",
      plain: true,
    });
    await loadWhitelistRules();
  } catch (error) {
    ElMessage.error({
      message: "操作失败",
      plain: true,
    });
  }
};

// 加载设置
const loadSettings = async () => {
  try {
    // 获取系统设置和前端设置
    const [systemData, frontendData] = await Promise.all([
      request("/api/admin/settings"),
      request("/api/frontend-settings"),
    ]);

    // 更新所有设置
    Object.assign(settings, {
      // 使用限制设置
      rpmLimit: systemData.rpmLimit ?? settings.rpmLimit,
      rtmLimit: systemData.rtmLimit ?? settings.rtmLimit,
      dailyLimit: systemData.dailyLimit ?? settings.dailyLimit,
      vipRpmLimit: systemData.vipRpmLimit ?? settings.vipRpmLimit,
      vipRtmLimit: systemData.vipRtmLimit ?? settings.vipRtmLimit,
      vipDailyLimit: systemData.vipDailyLimit ?? settings.vipDailyLimit,

      // 系统功能开关
      allowRegistration:
        systemData.allowRegistration ?? settings.allowRegistration,
      requireEmailVerification:
        systemData.requireEmailVerification ??
        settings.requireEmailVerification,
      allowLogin: systemData.allowLogin ?? settings.allowLogin,
      enableSystemLogs:
        systemData.enableSystemLogs ?? settings.enableSystemLogs,
      enableForbiddenWords:
        systemData.enableForbiddenWords ?? settings.enableForbiddenWords,

      // SMTP设置
      smtp: systemData.smtp ?? settings.smtp,

      // 签到设置
      signin_enabled: systemData.signin_enabled ?? settings.signin_enabled,
      signin_reward_type:
        systemData.signin_reward_type ?? settings.signin_reward_type,
      signin_reward_amount:
        systemData.signin_reward_amount ?? settings.signin_reward_amount,

      // 邀请设置
      invite_enabled: systemData.invite_enabled ?? settings.invite_enabled,
      inviter_reward_type:
        systemData.inviter_reward_type ?? settings.inviter_reward_type,
      inviter_reward_amount:
        systemData.inviter_reward_amount ?? settings.inviter_reward_amount,
      invitee_reward_type:
        systemData.invitee_reward_type ?? settings.invitee_reward_type,
      invitee_reward_amount:
        systemData.invitee_reward_amount ?? settings.invitee_reward_amount,

      // 前端设置
      frontend_logo: frontendData.logo || "",
      frontend_title: frontendData.title || "",
      frontend_vip_benefits: frontendData.vip_benefits || "",
      frontend_user_guide: frontendData.user_guide || "",
      enable_email_whitelist: systemData.enable_email_whitelist,
      // 卡密购买设置
      card_purchase_url: systemData.card_purchase_url ?? "",
      card_purchase_description: systemData.card_purchase_description ?? "",
      // 健康检查设置
      enable_health_check: systemData.enable_health_check ?? true,
      health_check_interval: systemData.health_check_interval ?? 5,
      health_check_batch_size: systemData.health_check_batch_size ?? 500,
    });
  } catch (error) {
    ElMessage.error({
      message: "加载设置失败",
      plain: true,
    });
    console.error({
      message: "加载设置失败:",
      error,
      plain: true,
    });
  }
};

// 保存设置
const saveSettings = async () => {
  if (
    !validateContent(settings.frontend_vip_benefits) ||
    !validateContent(settings.frontend_user_guide)
  ) {
    ElMessage.error({
      message: "内容包含不安全的HTML标签或属性",
      plain: true,
    });
    return;
  }
  saving.value = true;
  try {
    await Promise.all([
      // 保存系统设置
      request("/api/admin/settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          // 使用限制
          rpmLimit: settings.rpmLimit,
          rtmLimit: settings.rtmLimit,
          dailyLimit: settings.dailyLimit,
          vipRpmLimit: settings.vipRpmLimit,
          vipRtmLimit: settings.vipRtmLimit,
          vipDailyLimit: settings.vipDailyLimit,

          // 系统设置
          allowRegistration: settings.allowRegistration,
          requireEmailVerification: settings.requireEmailVerification,
          allowLogin: settings.allowLogin,
          enableSystemLogs: settings.enableSystemLogs,
          enableForbiddenWords: settings.enableForbiddenWords,

          // SMTP设置
          smtp: settings.smtp,

          // 签到设置
          signin_enabled: settings.signin_enabled,
          signin_reward_type: settings.signin_reward_type,
          signin_reward_amount: settings.signin_reward_amount,

          // 邀请设置
          invite_enabled: settings.invite_enabled,
          inviter_reward_type: settings.inviter_reward_type,
          inviter_reward_amount: settings.inviter_reward_amount,
          invitee_reward_type: settings.invitee_reward_type,
          invitee_reward_amount: settings.invitee_reward_amount,
          enable_email_whitelist: settings.enable_email_whitelist,
          // 卡密购买设置
          card_purchase_url: settings.card_purchase_url,
          card_purchase_description: settings.card_purchase_description,
          // 健康检查设置
          enable_health_check: settings.enable_health_check,
          health_check_interval: settings.health_check_interval,
          health_check_batch_size: settings.health_check_batch_size,
        }),
      }),

      // 保存前端设置
      request("/api/admin/frontend-settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: settings.frontend_title,
          vip_benefits: settings.frontend_vip_benefits,
          user_guide: settings.frontend_user_guide,
        }),
      }),
    ]);

    showSuccess.value = true;
    setTimeout(() => {
      showSuccess.value = false;
    }, 3000);
    ElMessage.success({
      message: "设置保存成功",
      plain: true,
    });
  } catch (error) {
    console.error("保存设置失败:", error);
    ElMessage.error({
      message: "保存设置失败",
      plain: true,
    });
  } finally {
    saving.value = false;
  }
};
// 测试SMTP
const testSmtp = async () => {
  testingSmtp.value = true;
  try {
    await request("/api/admin/settings/smtp/test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings.smtp),
    });
    ElMessage.success({
      message: "邮件测试成功",
      plain: true,
    });
  } catch (error) {
    ElMessage.error({
      message: "邮件测试失败",
      plain: true,
    });
  } finally {
    testingSmtp.value = false;
  }
};
// 加载违禁词列表
const loadForbiddenWords = async () => {
  try {
    const data = await request("/api/admin/forbidden-words");
    forbiddenWords.value = data;
  } catch (error) {
    ElMessage.error({
      message: "加载违禁词列表失败",
      plain: true,
    });
  }
};

// 添加违禁词
const addForbiddenWord = async () => {
  if (!newWord.word) {
    ElMessage.warning({
      message: "请输入违禁词",
      plain: true,
    });
    return;
  }

  try {
    await request("/api/admin/forbidden-words", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newWord),
    });

    ElMessage.success({
      message: "添加成功",
      plain: true,
    });
    newWord.word = "";
    newWord.description = "";
    await loadForbiddenWords();
  } catch (error) {
    ElMessage.error({
      message: "添加失败",
      plain: true,
    });
  }
};
// 删除违禁词
const deleteForbiddenWord = async (id) => {
  try {
    await request(`/api/admin/forbidden-words/${id}`, {
      method: "DELETE",
    });

    ElMessage.success({
      message: "删除成功",
      plain: true,
    });
    await loadForbiddenWords();
  } catch (error) {
    ElMessage.error({
      message: "删除失败",
      plain: true,
    });
  }
};

// 在组件挂载时加载数据
onMounted(() => {
  loadSettings();
  loadForbiddenWords();
  loadWhitelistRules(); // 添加这一行
});
</script>

<style>
/* 移动端滚动容器 */
.container {
  margin-bottom: 80px; /* 为固定底部按钮留出空间 */
}

@media (min-width: 768px) {
  .container {
    margin-bottom: 0;
  }
}
.preview-content {
  pointer-events: none;
}

.preview-content a {
  pointer-events: auto;
}

.prose {
  width: 100%;
  max-width: none !important;
}

.prose h1 {
  @apply text-2xl font-bold mt-6 mb-4;
}

.prose h2 {
  @apply text-xl font-bold mt-5 mb-3;
}

.prose h3 {
  @apply text-lg font-bold mt-4 mb-2;
}

.prose p {
  @apply my-3;
}

.prose ul {
  @apply list-disc list-inside my-3;
}

.prose ol {
  @apply list-decimal list-inside my-3;
}

.prose li {
  @apply my-1;
}

.prose code {
  @apply bg-gray-100 px-1 rounded;
}

.prose pre {
  @apply bg-gray-100 p-3 rounded my-3;
}

.prose blockquote {
  @apply border-l-4 border-gray-300 pl-4 my-3 italic;
}

.prose a {
  @apply text-blue-600 hover:text-blue-800 underline;
}
</style>
