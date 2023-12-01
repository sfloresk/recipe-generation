<!--
     Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
   
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
-->
<script setup>
import Header from './components/AppHeader.vue'
import Footer from './components/AppFooter.vue'
import '@aws-amplify/ui-vue/styles.css';
import { Authenticator } from '@aws-amplify/ui-vue';
import { fetchAuthSession } from 'aws-amplify/auth';

</script>

<template>
  <div style="margin-top:80px"></div>
  <authenticator v-slot="{ user, signOut }">
    <div class="container py-4 px-3 mx-auto">
      <Header @cognitoSignOut="signOut" />
      <div style="margin-top:20px">
      </div>


      <div class="container marketing">

        <!-- START THE FEATURETTES -->

        <div class="row featurette">
          <div class="col-md-7">
            <h2 class="featurette-heading fw-normal lh-1">Are you curious about how a dish is made?</h2>
            <p class="lead">Take a picture, and we will take care of the rest</p>
            <p class="small">EULA: Recipes are
   generated on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
              DO NOT USE THEM unless they are approved by a licensed professional. The system must be used with pictures containing only food and/or dishes. Any other use is prohibited</p>
              
              <p class="small">By using the system, you accept this end user license agreement.
            </p>
            <div class="form-check">
              <input v-model="isVegetarian" class="form-check-input" type="checkbox" value="" id="vegetarianCheck">
              <label class="form-check-label" for="vegetarianCheck">
                Vegetarian
              </label>
            </div>
            <div class="form-check">
              <input v-model="isGlutenFree" class="form-check-input" type="checkbox" value="" id="glutenFreeCheck">
              <label class="form-check-label" for="glutenFreeCheck">
                Gluten free
              </label>
            </div>
            <div class="form-check">
              <input v-model="isVegan" class="form-check-input" type="checkbox" value="" id="veganCheck">
              <label class="form-check-label" for="veganCheck">
                Vegan
              </label>
            </div>
            <div class="form-check">
              <input v-model=isNutFree class="form-check-input" type="checkbox">
              <label class="form-check-label" for="noNutsCheck">
                Nut free
              </label>
            </div>
            <p></p>
            <label for="cameraFileInput">
              <span class="btn btn-success">Get started!</span>

              <!-- The hidden file `input` for opening the native camera -->
              <input v-on:change="setImage" style="display: none;" id="cameraFileInput" type="file" accept="image/*" />
            </label>
            <p></p>

            <img id="selectedImg" v-if=current_image v-bind:src=current_image
              class="img-fluid border rounded-3 shadow-lg mb-4" loading="lazy" width="300" height="300">
          </div>
          <div class="col-md-5">
            <p v-if="processing_image" style="text-align: center;">
            <div class="text-center">
              <div class="spinner-border text-warning" role="status">
              </div>
            </div>
            <p>{{ loading_message }}</p>
            </p>
            <pre style="white-space: pre-wrap">
{{ generated_recipe }}
          </pre>

          </div>
        </div>


        <hr class="featurette-divider">

      </div>
      <Footer />
    </div>
  </authenticator>
</template>
<script>
export default {
  name: 'App',
  data: function () {
    return {
      current_image: null,
      loading_message: null,
      processing_image: false,
      current_image_base64: null,
      generated_recipe: '',
      isVegan: false,
      isVegetarian: false,
      isGlutenFree: false,
      isNutFree: false
    }
  },
  methods: {
    SetupHub() {
      Hub.listen('auth', (data) => {
        switch (data.payload.event) {
          case 'signIn':
            this.SetIsUserAuthenticated();
            break;
          case 'signUp':
            console.log('user signed up');
            break;
          case 'signOut':
            this.SetIsUserAuthenticated();
            break;
          case 'signIn_failure':
            console.log('user sign in failed');
            break;
          case 'configured':
            console.log('the Auth module is configured');
        }
      });
    },
    SetIsUserAuthenticated() {
      Auth.currentAuthenticatedUser({
        bypassCache: false // Optional, By default is false. If set to true, this call will send a request to Cognito to get the latest user data
      })
        .then((user) => this.isUserAuthenticated = true)
        .catch((err) => this.isUserAuthenticated = false);
    },
    readerOnLoad(result) {
      this.current_image_base64 = result;
      console.log("current_image_base64 set to " + this.current_image_base64)
    },
    setImage(event) {
      console.log("New image recieved")
      this.current_image = window.URL.createObjectURL(event.target.files[0])
      this.processing_image = true
      this.generated_recipe = ''
      this.startLoading()
      var reader = new FileReader();
      reader.readAsDataURL(event.target.files[0]);
      let vue_context = this
      reader.onload = function () {
        vue_context.current_image_base64 = reader.result.split(",")[1];
        console.log("Sending new image...")
        let constraints = {}
        let body
        constraints.isNutFree = vue_context.isNutFree
        constraints.isVegan = vue_context.isVegan
        constraints.isGlutenFree = vue_context.isGlutenFree
        constraints.isVegetarian = vue_context.isVegetarian
        body = JSON.stringify({
          "constraints": constraints,
          "image_b64": vue_context.current_image_base64
        })
        // Setting credentials
        async function currentSession() {
          try {
            const { accessToken, idToken } = (await fetchAuthSession()).tokens ?? {};
            return idToken.toString();
          } catch (err) {
            console.log(err);
            this.generated_recipe = "Invalid token, please sign in again"
          }
        }
        currentSession().then(idToken => {
          fetch("CHANGE_ME/dev/recipes", {
            "method": "POST",
            "body": body,
            "headers": {
              "Authorization": idToken
            }
          }).then(response => {
            if (response.ok) {
              return response.json()
            } else {
              console.log("Server returned " + response.status + " : " + response.statusText);
            }
          }).then(response => {
            console.log("Loading recipe...")
            console.log(response)
            vue_context.processing_image = false
            vue_context.generated_recipe = response.recipe_generation
          }).catch(err => {
            console.log(err);
            vue_context.generated_recipe = err + " Check your internet connection or sign in again"
            vue_context.processing_image = false
          });
        });
      }
      reader.onerror = function (error) {
        console.log('Error: ', error);
      };
    },
    startLoading() {
      if (this.processing_image) {

        if (!this.loading_message || this.loading_message === "Peeling carrots...") {
          this.loading_message = "Washing vegetables..."
        } else if (this.loading_message === "Washing vegetables...") {
          this.loading_message = "Chopping potatoes..."
        } else {
          this.loading_message = "Peeling carrots..."
        }
        setTimeout(this.startLoading, 3000)
      }
    },
  },

  watch: {
  }
}

</script>