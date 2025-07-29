fun properties(key: String) = providers.gradleProperty(key)
fun environment(key: String) = providers.environmentVariable(key)

plugins {
    id("com.intellij.java")
    id("org.jetbrains.intellij.platform") version "2.1.0"
    id("org.jetbrains.intellij.platform.migration") version "2.1.0"
    alias(libs.plugins.kotlin)
    alias(libs.plugins.apollo3)
}

group = properties("pluginGroup").get()
version = properties("pluginVersion").get()

// Configure project's dependencies
repositories {
    mavenCentral()
    gradlePluginPortal()

    intellijPlatform {
        defaultRepositories()
    }
}

// Dependencies are managed with Gradle version catalog - read more: https://docs.gradle.org/current/userguide/platforms.html#sub:version-catalog
dependencies {
    intellijPlatform {
        intellijIdeaCommunity("2024.1")

        bundledPlugin("com.intellij.java")
        plugin("org.jetbrains.kotlin.jvm:2.0.20")
        plugin("com.apollographql.apollo3:3.8.5")

        pluginVerifier()
        zipSigner()
        instrumentationTools()
    }
    implementation(libs.apolloRuntime)
    implementation(libs.jgit)
}

intellijPlatform {
    pluginConfiguration {
        version = "${project.version}"
        ideaVersion {
            sinceBuild = "242"
            untilBuild = "243.*"
        }
    }
}

kotlin {
    jvmToolchain(17)
}

java {
    sourceCompatibility = JavaVersion.VERSION_17
}

sourceSets {
    main {
        java.srcDir("src/main/java")
        kotlin.srcDir("src/main/kotlin")
    }
    test {
        java.srcDir("src/test/java")
        kotlin.srcDir("src/test/kotlin")
    }
}


apollo {
    service("service") {
        packageNamesFromFilePaths("org.jetbrains.plugin.template")
    }
}

tasks {
    wrapper {
        gradleVersion = properties("gradleVersion").get()
    }
}
