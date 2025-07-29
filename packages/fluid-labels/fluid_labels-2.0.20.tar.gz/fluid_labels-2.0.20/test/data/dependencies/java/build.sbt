def libraries = Seq(
  "com.typesafe.slick"        %% "slick"          % slickVersion,
  "com.typesafe.slick"        %% "slick-hikaricp" % slickVersion,
  "org.apache.logging.log4j"  %  "log4j-api"      % "2.17.0",
  "org.apache.logging.log4j"  %  "log4j-core"     % "2.2",
  "org.apache.logging.log4j"  %  "log4j-web"      % "2.2",
  "com.lmax"                  %  "disruptor"      % "3.3.2",
  "org.glassfish.jersey.core" %  "jersey-client"  % "2.17"
)

libraryDependencies += "org.apache.kylin" % "kylin" % "2.5.0"

libraryDependencies ++= Seq(
  "org.scalatest"            %% "scalatest"             % "2.2.4"   % "test,it",
  "org.mockito"              %  "mockito-all"           % "1.9.5"   % "test,it",
  "com.novocode"             %  "junit-interface"       % "0.7"     % "test->default",
  "org.pegdown"              %  "pegdown"               % "1.6.0"   % "test,it",
  "com.h2database"           %  "h2"                    % "1.4.200" % "test,it",
  "org.scala-lang"           %  "scala-compiler"        % scalaVersion.value,
  "org.scala-lang"           %  "scala-reflect"         % scalaVersion.value,
  "org.apache.nifi.registry" %  "nifi-registry-web-api" % "0.4.1"   % "nifi",
  "org.apache.nutch"         %  "nutch"                 % "2.0.0",
  "org.apache.ode"           %   "ode"                  % ode.version,
  "org.apache.openjpa"       %   "openjpa"              % "2.2.0"   % "test,it"
)

val akkaVersion: String = "2.5.25"

val akkaHttpVersion = "10.1.10"

def testingLibraries: Seq[ModuleID] =
  Seq(
    "com.typesafe.akka" %% "akka-testkit"       % akkaVersion     % "test",
    "com.typesafe.akka" %% "akka-http-testkit"  % akkaHttpVersion % "test",
    "org.scalatest"     %% "scalatest"          % "2.2.4"         % "test",
    "org.specs2"        %% "specs2"             % "2.3.11"        % "test",
    "com.novocode"       % "junit-interface"    % "0.7"           % "test->default",
    "org.mockito"        % "mockito-all"        % "1.9.5"         % "test",
    "org.pegdown"        % "pegdown"            % "1.6.0"         % Test
  )
