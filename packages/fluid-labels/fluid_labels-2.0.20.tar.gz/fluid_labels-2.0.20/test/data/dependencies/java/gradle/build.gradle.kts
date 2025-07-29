plugins {
    id("com.android.application")
    id("kotlin-android")
    id("kotlin-android-extensions")
}

android {
    compileSdkVersion(28)
    defaultConfig {
        applicationId = "sh.nothing.buildgradlekts"
        minSdkVersion(21)
        targetSdkVersion(28)
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    buildTypes.invoke {
        "release" {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}

dependencies {
    compile("org.codehaus.groovy:groovy:2.4.10")

    implementation(fileTree(mapOf("dir" to "libs", "include" to listOf("*.jar"))))
    implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk7:${rootProject.extra["kotlin_version"]}")

    // implementation("org.json:json:20160810")

    implementation("androidx.core:core-ktx:1.1.0-alpha03")
    implementation("androidx.constraintlayout:constraintlayout:1.1.3")
    implementation("com.google.android.material:material:1.0.0-beta01")

    /*
    implementation("ch.qos.logback:logback-core:1.2.3")
    implementation("ch.qos.logback:logback-classic:1.2.3")
    implementation("org.jetbrains.kotlin:kotlin-reflect:1.3.20")
    implementation("org.json:json:20160810")
    */

    implementation("org.jetbrains.kotlinx:kotlinx-html-js:0.8.0")
    implementation("org.jetbrains.kotlinx:kotlinx-html-js:0.8.0")
    implementation("io.springfox:springfox-swagger-ui:2.6.3")
    implementation("org.slf4j:slf4j-api:1.7.21")
    implementation(kotlin("stdlib", "1.3.20"))

    androidTestImplementation("androidx.test:runner:1.1.0-alpha4")
    testImplementation("junit:junit:4.12")
    testImplementation("org.junit.jupiter:junit-jupiter-api:5.6.2")
    testImplementation("io.kotest:kotest-runner-junit5-jvm:4.0.1")
    testImplementation("io.kotest:kotest-assertions-core-jvm:4.0.1")
    testImplementation("io.kotlintest:kotlintest-runner-junit5:3.3.1")
    testImplementation("org.junit.jupiter:junit-jupiter-api:$junitVersion")
    testImplementation("org.junit.jupiter:junit-jupiter-params:$junitVersion")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:5.6.2")

    compileClasspath("com.github.jengelman.gradle.plugins:shadow:4.0.4")

    runtime("org.junit.jupiter:junit-jupiter-engine:$junitVersion")
    runtimeOnly("io.kotest:kotest-core-jvm:4.0.1")
}
