# 简介

## HITSZ CTF Wiki
“让互联网发展成果惠及13亿中国人民”“没有网络安全就没有国家安全”“要紧紧牵住核心技术自主创新这个‘牛鼻子’”“深化国际合作，建立多边、民主、透明的国际互联网治理体系”……十八大以来，习近平总书记多次从保障网络安全、掌握核心技术、汇聚网络人才、清朗网络空间等方面部署网络强国建设。

近年来，网鼎杯（国家网络与信息安全信息通报中心 指导）、强网杯（中央网信办 指导）、蓝帽杯（公安部网络安全保卫局 指导）在各大高校和产业界中产生巨大影响力。

2021年是中国共产党建立100周年，也是习近平总书记在网络安全和信息化工作座谈会上发表重要讲话5周年。为了响应党和国家的号召，提升自身在信息技术时代的发展潜力，哈尔滨工业大学（深圳）的信息安全爱好者齐聚一堂，组建安全研究团队，结合学术科研和比赛经验编辑此文档。

## 声明

本网站基于原版的 CTF Wiki，仅供哈尔滨工业大学（深圳） CTF 爱好者内部学习使用。

原版 CTF Wiki 链接：https://ctf-wiki.org/

## 颜色主题

### 配色方案

根据浏览器与系统设置自动切换明暗主题，也可手动切换
<div class="tx-switch">
<button data-md-color-scheme="default"><code>Default</code></button>
<button data-md-color-scheme="slate"><code>Slate</code></button>
</div>
<script>
  var buttons = document.querySelectorAll("button[data-md-color-scheme]")
  Array.prototype.forEach.call(buttons, function(button) {
    button.addEventListener("click", function() {
      document.body.dataset.mdColorScheme = this.dataset.mdColorScheme;
      localStorage.setItem("data-md-color-scheme",this.dataset.mdColorScheme);
    })
  })
</script>

### 主色

点击色块可更换主题的主色
<div class="tx-switch">
<button data-md-color-primary="red"><code>Red</code></button>
<button data-md-color-primary="pink"><code>Pink</code></button>
<button data-md-color-primary="purple"><code>Purple</code></button>
<button data-md-color-primary="deep-purple"><code>Deep Purple</code></button>
<button data-md-color-primary="indigo"><code>Indigo</code></button>
<button data-md-color-primary="blue"><code>Blue</code></button>
<button data-md-color-primary="light-blue"><code>Light Blue</code></button>
<button data-md-color-primary="cyan"><code>Cyan</code></button>
<button data-md-color-primary="teal"><code>Teal</code></button>
<button data-md-color-primary="green"><code>Green</code></button>
<button data-md-color-primary="light-green"><code>Light Green</code></button>
<button data-md-color-primary="lime"><code>Lime</code></button>
<button data-md-color-primary="yellow"><code>Yellow</code></button>
<button data-md-color-primary="amber"><code>Amber</code></button>
<button data-md-color-primary="orange"><code>Orange</code></button>
<button data-md-color-primary="deep-orange"><code>Deep Orange</code></button>
<button data-md-color-primary="brown"><code>Brown</code></button>
<button data-md-color-primary="grey"><code>Grey</code></button>
<button data-md-color-primary="blue-grey"><code>Blue Grey</code></button>
<button data-md-color-primary="white"><code>White</code></button>
</div>
<script>
  var buttons = document.querySelectorAll("button[data-md-color-primary]");
  Array.prototype.forEach.call(buttons, function(button) {
    button.addEventListener("click", function() {
      document.body.dataset.mdColorPrimary = this.dataset.mdColorPrimary;
      localStorage.setItem("data-md-color-primary",this.dataset.mdColorPrimary);
    })
  })
</script>

### 辅助色

点击色块更换主题的辅助色
<div class="tx-switch">
<button data-md-color-accent="red"><code>Red</code></button>
<button data-md-color-accent="pink"><code>Pink</code></button>
<button data-md-color-accent="purple"><code>Purple</code></button>
<button data-md-color-accent="deep-purple"><code>Deep Purple</code></button>
<button data-md-color-accent="indigo"><code>Indigo</code></button>
<button data-md-color-accent="blue"><code>Blue</code></button>
<button data-md-color-accent="light-blue"><code>Light Blue</code></button>
<button data-md-color-accent="cyan"><code>Cyan</code></button>
<button data-md-color-accent="teal"><code>Teal</code></button>
<button data-md-color-accent="green"><code>Green</code></button>
<button data-md-color-accent="light-green"><code>Light Green</code></button>
<button data-md-color-accent="lime"><code>Lime</code></button>
<button data-md-color-accent="yellow"><code>Yellow</code></button>
<button data-md-color-accent="amber"><code>Amber</code></button>
<button data-md-color-accent="orange"><code>Orange</code></button>
<button data-md-color-accent="deep-orange"><code>Deep Orange</code></button>
</div>
<script>
  var buttons = document.querySelectorAll("button[data-md-color-accent]");
  Array.prototype.forEach.call(buttons, function(button) {
    button.addEventListener("click", function() {
      document.body.dataset.mdColorAccent = this.dataset.mdColorAccent;
      localStorage.setItem("data-md-color-accent",this.dataset.mdColorAccent);
    })
  })
</script>

<style>
button[data-md-color-accent]> code {
    background-color: var(--md-code-bg-color);
    color: var(--md-accent-fg-color);
  }
button[data-md-color-primary] > code {
    background-color: var(--md-code-bg-color);
    color: var(--md-primary-fg-color);
  }
button[data-md-color-primary='white'] > code {
    background-color: var(--md-primary-bg-color);
    color: var(--md-primary-fg-color);
  }
button[data-md-color-accent],button[data-md-color-primary],button[data-md-color-scheme]{
    width: 8.4rem;
    margin-bottom: .4rem;
    padding: 2.4rem .4rem .4rem;
    transition: background-color .25s,opacity .25s;
    border-radius: .2rem;
    color: #fff;
    font-size: .8rem;
    text-align: left;
    cursor: pointer;
}
button[data-md-color-accent]{
  background-color: var(--md-accent-fg-color);
}
button[data-md-color-primary]{
  background-color: var(--md-primary-fg-color);
}
button[data-md-color-scheme='default']{
  background-color: hsla(0, 0%, 100%, 1);
}
button[data-md-color-scheme='slate']{
  background-color: var(--md-default-bg-color);
}
button[data-md-color-accent]:hover, button[data-md-color-primary]:hover {
    opacity: .75;
}
</style>