<template>
  <div style="margin-top:-80px"></div>
  <header class="d-flex justify-content-between align-items-md-center pb-12 mb-12 border-bottom">
    <div class="d-flex flex-column flex-md-row align-items-center pb-12 mb-12 ">
      <a href="#" class="d-flex align-items-center link-body-emphasis text-decoration-none">
        <span class="fs-4">Recipe Generation</span>
      </a>
    </div>
    <nav class="d-inline-flex mt-2 mt-md-0 ms-md-auto">
        <a class="d-flex align-items-center link-body-emphasis text-decoration-none" v-on:click="cognitoSignOut" href="#">          
          <span class="fs-4">Sign out</span>
        </a>
      </nav>
      <div style="margin-top:80px"></div>
  </header>
</template>

<script>
export default {
 props: {
   username: String
 },
 methods: {
  cognitoSignOut() {
      console.log("Logging out user " + this.username)
      this.$emit('cognitoSignOut')
   }
 }
}
</script>