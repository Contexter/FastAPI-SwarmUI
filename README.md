#  Building the macOS SwiftUI “FastAPI-SwarmUI” application

Below is a step-to-finish, copy-and-paste-ready, sprint-based roadmap for building the macOS SwiftUI “FastAPI-SwarmUI” application. You’ll walk through:
1. Generating the Swift client from your existing OpenAPI spec
2. Bootstrapping a new Swift Package that contains both your UI and the generated client
3. Implementing GitController (shelling out to Git) for repo management and hooks
4. Building the SwiftUI views (sidebar, detail pane, ClientGen panel)
5. Wiring it all together so drag-and-drop, Git commits, and Swarm API calls work end-to-end
6. Packaging and running the App in Xcode

—

## Sprint 1 – Project Setup & OpenAPI Client Generation

**Goals**
- Create a new Swift Package for “FastAPISwarmUI”
- Install OpenAPI Generator CLI
- Generate a Swift client (OrchestratorClient) from your FastAPI’s OpenAPI JSON
- Integrate that client into your new Swift Package

**Prerequisites**
- Xcode 14.3 (or later)
- Homebrew (for installing the OpenAPI Generator CLI)
- Your FastAPI’s OpenAPI JSON (we’ll call it `orchestrator-openapi.json`) saved locally

### 1.1 Install OpenAPI Generator CLI

Open Terminal and run:
```bash
brew install openapi-generator
```
If you already have it, skip this step. Otherwise, verify with:
```bash
openapi-generator version
```

### 1.2 Save your OpenAPI JSON

Create a folder for your overall project:
```bash
mkdir ~/FastAPISwarmUI
cd ~/FastAPISwarmUI
```

Inside that folder, create a file called `orchestrator-openapi.json` and paste your entire FastAPI OpenAPI definition into it. For example:


```bash
cat > orchestrator-openapi.json <<EOF
{
  "openapi":"3.1.0",
  "info":{"title":"FountainAI Orchestrator API","version":"1.0.0"},
  "paths": {
    "/v1/health": {
      "get": {
        "tags":["Orchestrator"],
        "summary":"Health",
        "operationId":"health_v1_health_get",
        "responses": {
          "200": {
            "description":"Successful Response",
            "content": {
              "application/json":{
                "schema":{"$ref":"#/components/schemas/HealthResponse"}
              }
            }
          }
        }
      }
    },
    "/v1/services": {
      "get": {
        "tags":["Orchestrator"],
        "summary":"List Services",
        "operationId":"list_services_v1_services_get",
        "parameters":[
          {
            "name":"limit","in":"query","required":false,
            "schema":{"type":"integer","minimum":1,"default":50}
          },
          {
            "name":"offset","in":"query","required":false,
            "schema":{"type":"integer","minimum":0,"default":0}
          },
          {
            "name":"status","in":"query","required":false,
            "schema":{
              "anyOf":[
                {"type":"string","pattern":"^(running|updating|error)$"},
                {"type":"null"}
              ]
            }
          }
        ],
        "responses":{
          "200":{
            "description":"Successful Response",
            "content":{
              "application/json":{
                "schema":{"$ref":"#/components/schemas/ServiceListResponse"}
              }
            }
          },
          "422":{ "description":"Validation Error" }
        }
      },
      "post":{
        "tags":["Orchestrator"],
        "summary":"Create Service",
        "operationId":"create_service_v1_services_post",
        "parameters":[
          {
            "name":"name","in":"query","required":true,
            "schema":{"type":"string"}
          }
        ],
        "requestBody":{
          "required":true,
          "content":{
            "application/json":{
              "schema":{"$ref":"#/components/schemas/ServiceSpec"}
            }
          }
        },
        "responses":{
          "201":{
            "description":"Successful Response",
            "content":{
              "application/json":{
                "schema":{"$ref":"#/components/schemas/ServiceDetail"}
              }
            }
          },
          "422":{ "description":"Validation Error" }
        }
      }
    },
    "/v1/services/{service}": {
      "get": {
        "tags":["Orchestrator"],
        "summary":"Get Service",
        "operationId":"get_service_v1_services__service__get",
        "parameters":[
          {
            "name":"service","in":"path","required":true,
            "schema":{"type":"string"}
          }
        ],
        "responses":{
          "200":{
            "description":"Successful Response",
            "content":{
              "application/json":{
                "schema":{"$ref":"#/components/schemas/ServiceDetail"}
              }
            }
          },
          "404":{
            "content":{"application/json":{"schema":{"$ref":"#/components/schemas/ErrorResponse"}}},
            "description":"Not Found"
          },
          "422":{ "description":"Validation Error" }
        }
      },
      "delete": {
        "tags":["Orchestrator"],
        "summary":"Delete Service",
        "operationId":"delete_service_v1_services__service__delete",
        "parameters":[
          {
            "name":"service","in":"path","required":true,
            "schema":{"type":"string"}
          }
        ],
        "responses":{
          "204":{ "description":"Successful Response" },
          "404":{
            "content":{"application/json":{"schema":{"$ref":"#/components/schemas/ErrorResponse"}}},
            "description":"Not Found"
          },
          "422":{ "description":"Validation Error" }
        }
      }
    },
    "/v1/services/{service}/deploy": {
      "post":{
        "tags":["Orchestrator"],
        "summary":"Deploy Service",
        "operationId":"deploy_service_v1_services__service__deploy_post",
        "parameters":[
          {
            "name":"service","in":"path","required":true,
            "schema":{"type":"string"}
          }
        ],
        "responses":{
          "200":{
            "description":"Successful Response",
            "content":{
              "application/json":{
                "schema":{"$ref":"#/components/schemas/DeployResponse"}
              }
            }
          },
          "404":{
            "content":{"application/json":{"schema":{"$ref":"#/components/schemas/ErrorResponse"}}},
            "description":"Not Found"
          },
          "422":{ "description":"Validation Error" }
        }
      }
    },
    "/v1/deploy": {
      "post":{
        "tags":["Orchestrator"],
        "summary":"Batch Deploy",
        "operationId":"batch_deploy_v1_deploy_post",
        "requestBody":{
          "required":true,
          "content":{
            "application/json":{
              "schema":{"$ref":"#/components/schemas/DeployRequest"}
            }
          }
        },
        "responses":{
          "200":{
            "description":"Successful Response",
            "content":{
              "application/json":{
                "schema":{"$ref":"#/components/schemas/BatchDeployResponse"}
              }
            }
          },
          "400":{
            "description":"Bad Request",
            "content":{
              "application/json":{
                "schema":{"$ref":"#/components/schemas/ErrorResponse"}
              }
            }
          },
          "422":{ "description":"Validation Error" }
        }
      }
    },
    "/v1/services/{service}/config": {
      "get": {
        "tags":["Orchestrator"],
        "summary":"Get Config",
        "operationId":"get_config_v1_services__service__config_get",
        "parameters":[
          {
            "name":"service","in":"path","required":true,
            "schema":{"type":"string"}
          }
        ],
        "responses":{
          "200":{
            "description":"Successful Response",
            "content":{
              "application/json":{
                "schema":{"$ref":"#/components/schemas/ConfigDetail"}
              }
            }
          },
          "404":{
            "content":{"application/json":{"schema":{"$ref":"#/components/schemas/ErrorResponse"}}},
            "description":"Not Found"
          },
          "422":{ "description":"Validation Error" }
        }
      },
      "patch": {
        "tags":["Orchestrator"],
        "summary":"Patch Config",
        "operationId":"patch_config_v1_services__service__config_patch",
        "parameters":[
          {
            "name":"service","in":"path","required":true,
            "schema":{"type":"string"}
          }
        ],
        "requestBody":{
          "required":true,
          "content":{
            "application/json":{
              "schema":{"$ref":"#/components/schemas/ConfigPatch"}
            }
          }
        },
        "responses":{
          "200":{
            "description":"Successful Response",
            "content":{
              "application/json":{
                "schema":{"$ref":"#/components/schemas/ConfigDetail"}
              }
            }
          },
          "404":{
            "content":{"application/json":{"schema":{"$ref":"#/components/schemas/ErrorResponse"}}},
            "description":"Not Found"
          },
          "422":{ "description":"Validation Error" }
        }
      }
    },
    "/v1/services/{service}/logs": {
      "get":{
        "tags":["Orchestrator"],
        "summary":"Get Logs",
        "operationId":"get_logs_v1_services__service__logs_get",
        "parameters":[
          {
            "name":"service","in":"path","required":true,
            "schema":{"type":"string"}
          },
          {
            "name":"tail","in":"query","required":false,
            "schema":{"type":"integer","minimum":1,"default":100}
          }
        ],
        "responses":{
          "200":{
            "description":"Successful Response",
            "content":{"text/plain":{"schema":{"type":"string"}}}
          },
          "404":{
            "content":{"text/plain":{"schema":{"$ref":"#/components/schemas/ErrorResponse"}}},
            "description":"Not Found"
          },
          "422":{ "description":"Validation Error" }
        }
      }
    },
    "/v1/services/{service}/rollback": {
      "post":{
        "tags":["Orchestrator"],
        "summary":"Rollback Service",
        "operationId":"rollback_service_v1_services__service__rollback_post",
        "parameters":[
          {
            "name":"service","in":"path","required":true,
            "schema":{"type":"string"}
          }
        ],
        "responses":{
          "200":{
            "description":"Successful Response",
            "content":{
              "application/json":{
                "schema":{"$ref":"#/components/schemas/DeployResponse"}
              }
            }
          },
          "404":{
            "content":{"application/json":{"schema":{"$ref":"#/components/schemas/ErrorResponse"}}},
            "description":"Not Found"
          },
          "422":{ "description":"Validation Error" }
        }
      }
    },
    "/v1/clientgen/{service}/regenerate": {
      "post":{
        "tags":["ClientGen"],
        "summary":"Regenerate Client",
        "operationId":"regenerate_client_v1_clientgen__service__regenerate_post",
        "parameters":[
          {
            "name":"service","in":"path","required":true,
            "schema":{"type":"string"}
          }
        ],
        "responses":{
          "200":{
            "description":"Successful Response",
            "content":{
              "application/json":{
                "schema":{"$ref":"#/components/schemas/ClientStatusResponse"}
              }
            }
          },
          "404":{
            "content":{"application/json":{"schema":{"$ref":"#/components/schemas/ErrorResponse"}}},
            "description":"Not Found"
          },
          "422":{ "description":"Validation Error" }
        }
      }
    },
    "/v1/clientgen/status/{service}": {
      "get":{
        "tags":["ClientGen"],
        "summary":"Get Client Status",
        "operationId":"get_client_status_v1_clientgen_status__service__get",
        "parameters":[
          {
            "name":"service","in":"path","required":true,
            "schema":{"type":"string"}
          }
        ],
        "responses":{
          "200":{
            "description":"Successful Response",
            "content":{
              "application/json":{
                "schema":{"$ref":"#/components/schemas/ClientStatusResponse"}
              }
            }
          },
          "404":{
            "content":{"application/json":{"schema":{"$ref":"#/components/schemas/ErrorResponse"}}},
            "description":"Not Found"
          },
          "422":{ "description":"Validation Error" }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "BatchDeployResponse":{
        "type":"object",
        "additionalProperties":{"$ref":"#/components/schemas/DeployResponse"}
      },
      "ClientStatusResponse":{
        "type":"object",
        "required":["service","last_generated_at","checksum","status"],
        "properties":{
          "service":{"type":"string"},
          "last_generated_at":{"type":"string","format":"date-time"},
          "checksum":{"type":"string"},
          "status":{"type":"string"},
          "error":{"anyOf":[{"type":"string"},{"type":"null"}]}
        }
      },
      "ConfigDetail":{
        "type":"object",
        "required":["env","ports"],
        "properties":{
          "env":{"type":"object","additionalProperties":{"type":"string"}},
          "ports":{"type":"object","additionalProperties":{"type":"integer"}}
        }
      },
      "ConfigPatch":{
        "type":"object",
        "properties":{
          "env":{"anyOf":[{"type":"object","additionalProperties":{"type":"string"}},{"type":"null"}]},
          "ports":{"anyOf":[{"type":"object","additionalProperties":{"type":"integer"}},{"type":"null"}]}
        }
      },
      "ConfigReference":{
        "type":"object",
        "required":["name","target"],
        "properties":{
          "name":{"type":"string"},
          "target":{"type":"string"}
        }
      },
      "DeployRequest":{
        "type":"object",
        "required":["services"],
        "properties":{
          "services":{"type":"array","items":{"type":"string"}}
        }
      },
      "DeployResponse":{
        "type":"object",
        "required":["status","message"],
        "properties":{
          "status":{"type":"string"},
          "message":{"type":"string"}
        }
      },
      "ErrorResponse":{
        "type":"object",
        "required":["code","message"],
        "properties":{
          "code":{"type":"integer"},
          "message":{"type":"string"}
        }
      },
      "HealthResponse":{
        "type":"object",
        "required":["status","uptime"],
        "properties":{
          "status":{"type":"string"},
          "uptime":{"type":"string","format":"date-time"}
        }
      },
      "ServiceDetail":{
        "type":"object",
        "required":["name","status","ports","secrets","configs"],
        "properties":{
          "name":{"type":"string"},
          "status":{"type":"string"},
          "ports":{"type":"object","additionalProperties":{"type":"integer"}},
          "secrets":{"type":"array","items":{"type":"string"}},
          "configs":{"type":"array","items":{"$ref":"#/components/schemas/ConfigReference"}}
        }
      },
      "ServiceListResponse":{
        "type":"object",
        "required":["services","total","limit","offset"],
        "properties":{
          "services":{"type":"array","items":{"$ref":"#/components/schemas/ServiceDetail"}},
          "total":{"type":"integer"},
          "limit":{"type":"integer"},
          "offset":{"type":"integer"}
        }
      },
      "ServiceSpec":{
        "type":"object",
        "required":["image"],
        "properties":{
          "image":{"type":"string"},
          "ports":{"anyOf":[{"type":"object","additionalProperties":{"type":"integer"}},{"type":"null"}],"default":{}},
          "secrets":{"anyOf":[{"type":"array","items":{"type":"string"}},{"type":"null"}],"default":[]},
          "configs":{"anyOf":[{"type":"array","items":{"$ref":"#/components/schemas/ConfigReference"}},{"type":"null"}],"default":[]}
        }
      },
      "ValidationError":{
        "type":"object",
        "required":["loc","msg","type"],
        "properties":{
          "loc":{"type":"array","items":{"anyOf":[{"type":"string"},{"type":"integer"}]}},
          "msg":{"type":"string"},
          "type":{"type":"string"}
        }
      },
      "HTTPValidationError":{
        "type":"object",
        "properties":{
          "detail":{"type":"array","items":{"$ref":"#/components/schemas/ValidationError"}}
        }
      }
    }
  }
}
EOF
```

Tip: Make sure that JSON is syntactically valid (you can run jq . orchestrator-openapi.json if you have jq installed).

### 1.3 Generate the Swift Client

From within `~/FastAPISwarmUI`, run:
```bash
openapi-generator generate \
  -i orchestrator-openapi.json \
  -g swift5 \
  -o GeneratedOrchestratorClient \
  --additional-properties=primaryLanguage=Swift,projectName=OrchestratorClient,firstTagLowerCase=true
```

After a moment, you’ll see a new folder:
```
~/FastAPISwarmUI/GeneratedOrchestratorClient
```
Inside it:
```
GeneratedOrchestratorClient/
├── Package.swift
├── README.md
└── Sources/
    └── OrchestratorClient/
        ├── APIs/
        │   ├── DefaultAPI.swift
        │   ├── OrchestratorAPIs.swift
        │   └── ClientGenAPIs.swift
        ├── Models/
        │   ├── HealthResponse.swift
        │   ├── ServiceSpec.swift
        │   ├── ServiceDetail.swift
        │   ├── ServiceListResponse.swift
        │   ├── DeployRequest.swift
        │   ├── DeployResponse.swift
        │   ├── ConfigDetail.swift
        │   ├── ConfigPatch.swift
        │   ├── ClientStatusResponse.swift
        │   └── ErrorResponse.swift
        └── ...
```

Open `GeneratedOrchestratorClient/Package.swift` in Xcode or a text editor to confirm its contents:
```swift
// swift-tools-version:5.7
import PackageDescription

let package = Package(
    name: "OrchestratorClient",
    platforms: [
        .macOS(.v12)
    ],
    products: [
        .library(
            name: "OrchestratorClient",
            targets: ["OrchestratorClient"]
        ),
    ],
    dependencies: [
        // No external dependencies; uses URLSession internally
    ],
    targets: [
        .target(
            name: "OrchestratorClient",
            dependencies: [],
            path: "Sources/OrchestratorClient",
            swiftSettings: [
                .define("RELEASE")
            ]
        ),
        .testTarget(
            name: "OrchestratorClientTests",
            dependencies: ["OrchestratorClient"],
            path: "Tests/OrchestratorClientTests"
        ),
    ]
)
```

### 1.4 Create the Root Swift Package for “FastAPISwarmUI”

In `~/FastAPISwarmUI`, create a new `Package.swift`:
```bash
cat > Package.swift <<EOF
// swift-tools-version:5.7
import PackageDescription

let package = Package(
    name: "FastAPISwarmUI",
    platforms: [
        .macOS(.v12)
    ],
    products: [
        .executable(
            name: "FastAPISwarmUI",
            targets: ["FastAPISwarmUI"]
        ),
        .library(
            name: "OrchestratorClient",
            targets: ["OrchestratorClient"]
        )
    ],
    dependencies: [
        // Add any third-party Swift packages later if needed
    ],
    targets: [
        .executableTarget(
            name: "FastAPISwarmUI",
            dependencies: [
                "OrchestratorClient"
            ],
            path: "Sources/FastAPISwarmUI"
        ),
        .target(
            name: "OrchestratorClient",
            dependencies: [],
            path: "Sources/OrchestratorClient"
        )
    ]
)
EOF
```

Now, organize directories under `~/FastAPISwarmUI`:
```bash
mkdir -p Sources/OrchestratorClient
mkdir -p Sources/FastAPISwarmUI
```

Copy the generated client into `Sources/OrchestratorClient`:
```bash
# Remove any leftover placeholder folder
rm -rf Sources/OrchestratorClient/*
# Copy everything from GeneratedOrchestratorClient/Sources/OrchestratorClient
cp -R GeneratedOrchestratorClient/Sources/OrchestratorClient/* Sources/OrchestratorClient/
```

At this point, your folder tree should look like:
```
~/FastAPISwarmUI/
├── Package.swift
├── orchestrator-openapi.json
├── GeneratedOrchestratorClient/
│   ├── Package.swift
│   └── Sources/OrchestratorClient/…
└── Sources/
    ├── FastAPISwarmUI/       ← (currently empty)
    └── OrchestratorClient/   ← (paste of generated code)
```

### 1.5 Open in Xcode & Verify
1. In Terminal:
   ```bash
   open Package.swift
   ```
2. Xcode will prompt to “Open Swift Package”; confirm.
3. In the Project navigator, you should see two targets:
   - FastAPISwarmUI (empty for now)
   - OrchestratorClient (with Generated models & APIs)
4. Build (⌘B). You should get **Build Succeeded** (despite having no code in FastAPISwarmUI yet).

At the end of Sprint 1, you have:
- A Swift Package with an OrchestratorClient library generated from your OpenAPI
- An empty FastAPISwarmUI executable target ready for you to start building your macOS SwiftUI app

—

## Sprint 2 – GitController & Workspace Management

**Goals**
- Create a `GitController.swift` that shells out to `/usr/bin/git`
- Implement functions to:
  1. Detect or initialize a Git repo
  2. Stage & commit changes
  3. Install a post-commit hook that calls your FastAPI `/v1/services/{service}/deploy`
  4. Check for uncommitted changes & current branch
- Create a `WorkspaceController.swift` to handle drag-and-drop import of FastAPI folders

### 2.1 Create GitController.swift

In Xcode, select the FastAPISwarmUI target, and under `Sources/FastAPISwarmUI`, create a new file named `GitController.swift` with this content:
```swift
import Foundation

enum GitError: Error {
    case commandFailed(String)
}

/// A utility class to run Git commands in a given directory.
struct GitController {

    /// Run a Git command in `directory`, returning stdout (trimmed), or throwing `GitError` on nonzero exit.
    @discardableResult
    static func runGitCommand(in directory: URL, arguments: [String]) throws -> String {
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/git")
        process.currentDirectoryURL = directory
        process.arguments = arguments

        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe

        try process.run()
        process.waitUntilExit()

        let data = pipe.fileHandleForReading.readDataToEndOfFile()
        let output = String(decoding: data, as: UTF8.self)

        if process.terminationStatus != 0 {
            throw GitError.commandFailed(output)
        }
        return output.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    /// If `folder` has a .git, return its current branch & commit SHA.
    /// Otherwise, `git init`, `git add .`, `git commit -m "Initial import"`, and return "main" & its SHA.
    static func initializeOrAdoptRepo(at folder: URL) -> (currentBranch: String, lastCommitSHA: String) {
        let gitFolder = folder.appendingPathComponent(".git", isDirectory: true)
        do {
            if FileManager.default.fileExists(atPath: gitFolder.path) {
                // Already a Git repo
                let branch = try runGitCommand(in: folder, arguments: ["rev-parse", "--abbrev-ref", "HEAD"])
                let commit = try runGitCommand(in: folder, arguments: ["rev-parse", "HEAD"])
                return (branch, commit)
            } else {
                // Not a repo yet: init & commit everything
                _ = try runGitCommand(in: folder, arguments: ["init"])
                _ = try runGitCommand(in: folder, arguments: ["add", "."])
                _ = try runGitCommand(in: folder, arguments: ["commit", "-m", "Initial import"])
                let branch = try runGitCommand(in: folder, arguments: ["rev-parse", "--abbrev-ref", "HEAD"])
                let commit = try runGitCommand(in: folder, arguments: ["rev-parse", "HEAD"])
                return (branch, commit)
            }
        } catch {
            print("Git initialization/adoption failed: \(error)")
            return ("unknown", "unknown")
        }
    }

    /// Install a `post-commit` hook in `<folder>/.git/hooks/post-commit` that calls the Orchestrator API to deploy.
    static func installGitHooks(at folder: URL) {
        let hooksDir = folder.appendingPathComponent(".git/hooks", isDirectory: true)
        do {
            // Ensure hooks directory exists
            try FileManager.default.createDirectory(at: hooksDir, withIntermediateDirectories: true, attributes: nil)

            let projectName = folder.lastPathComponent
            let postCommitHook = """
            #!/bin/sh
            # post-commit hook: after each commit, notify the FastAPI Swarm Orchestrator
            PROJECT_NAME="\(projectName)"
            COMMIT_SHA=$(git rev-parse HEAD)
            curl -X POST \\
              "http://localhost:8000/v1/services/${PROJECT_NAME}/deploy" \\
              -H "Content-Type: application/json"
            """
            let hookURL = hooksDir.appendingPathComponent("post-commit")
            try postCommitHook.write(to: hookURL, atomically: true, encoding: .utf8)

            // Make script executable
            var attributes = try FileManager.default.attributesOfItem(atPath: hookURL.path)
            attributes[.posixPermissions] = 0o755
            try FileManager.default.setAttributes(attributes, ofItemAtPath: hookURL.path)
        } catch {
            print("Failed to install Git hook: \(error)")
        }
    }

    /// Stage all changes and commit with `message`.
    static func commitAllChanges(in folder: URL, message: String) throws {
        _ = try runGitCommand(in: folder, arguments: ["add", "."])
        _ = try runGitCommand(in: folder, arguments: ["commit", "-m", message])
    }

    /// Check if there are uncommitted changes (`git status --porcelain` nonempty).
    static func hasUncommittedChanges(in folder: URL) -> Bool {
        do {
            let output = try runGitCommand(in: folder, arguments: ["status", "--porcelain"])
            return !output.isEmpty
        } catch {
            return false
        }
    }

    /// Return the current branch name (`git rev-parse --abbrev-ref HEAD`).
    static func currentBranch(in folder: URL) -> String {
        do {
            return try runGitCommand(in: folder, arguments: ["rev-parse", "--abbrev-ref", "HEAD"])
        } catch {
            return "unknown"
        }
    }

    /// Return the latest commit SHA (`git rev-parse HEAD`).
    static func lastCommitSHA(in folder: URL) -> String {
        do {
            return try runGitCommand(in: folder, arguments: ["rev-parse", "HEAD"])
        } catch {
            return "unknown"
        }
    }
}
```
⏸ **Explanation of key methods:**
- **`runGitCommand(in:arguments:)`**: wraps shelling out to git, throwing if exit code ≠ 0.
- **`initializeOrAdoptRepo(at:)`**: if `<folder>/.git` exists, returns its branch/commit. Otherwise, runs `git init`, stages everything, and makes an initial commit.
- **`installGitHooks(at:)`**: writes a `post-commit` script under `.git/hooks/` that posts to your FastAPI’s `/v1/services/{projectName}/deploy`.
- **`commitAllChanges(in:message:)`**: runs `git add .` and `git commit -m` for you.
- **`hasUncommittedChanges(in:)`, `currentBranch(in:)`, `lastCommitSHA(in:)`**: small helpers for status polling.

### 2.2 Create WorkspaceController.swift

In `Sources/FastAPISwarmUI`, create a file named `WorkspaceController.swift`. Paste:
```swift
import Foundation
import AppKit

/// Represents one FastAPI app “project” copied into the workspace.
struct ManagedApp: Identifiable {
    let id = UUID()
    let localURL: URL         // e.g. ~/FastAPISwarmUI/ManagedApps/MyService
    var name: String          // “MyService”
    var currentBranch: String // e.g. “main”
    var lastCommitSHA: String // e.g. “a1b2c3d4…”
    var hasUncommittedChanges: Bool
}

/// Manages a workspace directory where every dropped FastAPI folder is copied & versioned.
class WorkspaceController: ObservableObject {
    @Published var managedApps: [ManagedApp] = []

    /// The root workspace folder (~/FastAPISwarmUI/ManagedApps)
    let workspaceRoot: URL

    init() {
        let home = FileManager.default.homeDirectoryForCurrentUser
        self.workspaceRoot = home.appendingPathComponent("FastAPISwarmUI/ManagedApps", isDirectory: true)

        // Ensure workspace exists
        try? FileManager.default.createDirectory(at: workspaceRoot, withIntermediateDirectories: true, attributes: nil)

        // On launch, scan existing subfolders and populate `managedApps`
        scanWorkspace()
    }

    /// Scan each subdirectory in workspaceRoot and load its Git info.
    func scanWorkspace() {
        managedApps.removeAll()

        guard let subfolders = try? FileManager.default.contentsOfDirectory(at: workspaceRoot,
                                                                            includingPropertiesForKeys: [.isDirectoryKey],
                                                                            options: [.skipsHiddenFiles]) else {
            return
        }

        for folder in subfolders {
            var isDir: ObjCBool = false
            if FileManager.default.fileExists(atPath: folder.path, isDirectory: &isDir), isDir.boolValue {
                let branch = GitController.currentBranch(in: folder)
                let sha = GitController.lastCommitSHA(in: folder)
                let hasChanges = GitController.hasUncommittedChanges(in: folder)
                let app = ManagedApp(localURL: folder,
                                     name: folder.lastPathComponent,
                                     currentBranch: branch,
                                     lastCommitSHA: sha,
                                     hasUncommittedChanges: hasChanges)
                managedApps.append(app)
            }
        }
    }

    /// Copy `originalURL` (a user-dropped folder) into the workspace, initializing Git, installing hooks, and re-scanning.
    func importFastAPIFolder(at originalURL: URL) {
        do {
            let fm = FileManager.default

            // Destination folder name (avoid collisions by appending timestamp if needed)
            var destName = originalURL.lastPathComponent
            var destURL = workspaceRoot.appendingPathComponent(destName, isDirectory: true)

            if fm.fileExists(atPath: destURL.path) {
                // If name exists, append a timestamp suffix
                let timestamp = ISO8601DateFormatter().string(from: Date())
                destName = "\(destName)-\(timestamp)"
                destURL = workspaceRoot.appendingPathComponent(destName, isDirectory: true)
            }

            // Copy entire folder
            try fm.copyItem(at: originalURL, to: destURL)

            // Initialize/adopt Git repo
            _ = GitController.initializeOrAdoptRepo(at: destURL)

            // Install post-commit Git hook
            GitController.installGitHooks(at: destURL)

            // Refresh `managedApps`
            scanWorkspace()
        } catch {
            print("Error importing folder: \(error)")
        }
    }

    /// Remove a managed app (deletes its folder from disk and refreshes).
    func removeManagedApp(_ app: ManagedApp) {
        do {
            try FileManager.default.removeItem(at: app.localURL)
        } catch {
            print("Error removing app: \(error)")
        }
        scanWorkspace()
    }
}
```
⏸ **Explanation:**
- **`ManagedApp`**: holds metadata (URL, name, branch, commit, uncommitted-changes flag).
- **`WorkspaceController`:**
  - On `init()`, ensures `~/FastAPISwarmUI/ManagedApps` exists and calls `scanWorkspace()`.
  - `scanWorkspace()` loops over subfolders, queries Git for branch/commit/dirty status, and populates `managedApps`.
  - `importFastAPIFolder(at:)` copies a dropped folder into `ManagedApps/`, runs `initializeOrAdoptRepo()`, installs Git hooks, and re-scans.
  - `removeManagedApp(_:)` deletes the folder and re-scans.

At the end of Sprint 2, you have:
- A GitController that can init repos, commit, install hooks, and query status.
- A WorkspaceController that manages your `ManagedApps` folder and responds to drag-and-drop imports.

—

## Sprint 3 – Basic SwiftUI: Drag-and-Drop & Sidebar

**Goals**
- Build a SwiftUI window that:
  1. Accepts folder drops
  2. Shows a sidebar `List` of `ManagedApp` items
  3. Reflects Git status (branch + dirty indicator)
  4. Provides a “Remove” action
- Wire the drag-and-drop call to `WorkspaceController.importFastAPIFolder(at:)`

### 3.1 Create ContentView.swift

In `Sources/FastAPISwarmUI`, create `ContentView.swift` with:
```swift
import SwiftUI

struct ContentView: View {
    @StateObject private var workspace = WorkspaceController()
    @State private var selectedApp: ManagedApp?

    var body: some View {
        NavigationView {
            VStack {
                Text("Drop a FastAPI folder here to manage it")
                    .frame(maxWidth: .infinity, minHeight: 100)
                    .padding()
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.gray, lineWidth: 2)
                    )
                    .onDrop(of: [.fileURL], isTargeted: nil, perform: handleDrop(providers:))

                List(selection: $selectedApp) {
                    ForEach(workspace.managedApps) { app in
                        HStack {
                            VStack(alignment: .leading) {
                                Text(app.name)
                                    .font(.headline)
                                Text("Branch: \(app.currentBranch)")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            Spacer()
                            if app.hasUncommittedChanges {
                                Circle()
                                    .fill(Color.red)
                                    .frame(width: 10, height: 10)
                                    .help("Uncommitted changes")
                            }
                        }
                        .tag(app)
                    }
                    .onDelete(perform: deleteItems)
                }
                .listStyle(SidebarListStyle())
                .frame(minWidth: 200)
            }
            .frame(minWidth: 300)
        }
        .frame(minWidth: 800, minHeight: 600)
    }

    /// Handle dropped folder(s)
    private func handleDrop(providers: [NSItemProvider]) -> Bool {
        for provider in providers {
            if provider.hasItemConformingToTypeIdentifier("public.file-url") {
                provider.loadItem(forTypeIdentifier: "public.file-url", options: nil) { (item, error) in
                    DispatchQueue.main.async {
                        guard
                            let data = item as? Data,
                            let url = URL(dataRepresentation: data, relativeTo: nil),
                            url.hasDirectoryPath
                        else {
                            return
                        }
                        workspace.importFastAPIFolder(at: url)
                    }
                }
                return true
            }
        }
        return false
    }

    /// Remove apps from the workspace
    private func deleteItems(offsets: IndexSet) {
        for index in offsets {
            let app = workspace.managedApps[index]
            workspace.removeManagedApp(app)
        }
    }
}
```
⏸ **Highlights:**
- The top “Drop a FastAPI folder here” box uses `.onDrop(of: [.fileURL])` to receive folder URLs.
- Inside `handleDrop`, once we confirm `url.hasDirectoryPath`, we call `workspace.importFastAPIFolder(at: url)`.
- Below, a `List(selection:)` displays `workspace.managedApps`, showing each `app.name` and `app.currentBranch`.
- If `app.hasUncommittedChanges` is true, we draw a small red dot.
- Swipe-to-delete (⌫) is enabled via `.onDelete(perform:)`, calling `workspace.removeManagedApp(_:)`.

### 3.2 Update the App Entry Point

In `Sources/FastAPISwarmUI`, create `FastAPISwarmUIApp.swift`:
```swift
import SwiftUI

@main
struct FastAPISwarmUIApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```
This tells Swift that `ContentView` is your main window.

### 3.3 Run & Test Drag-and-Drop
1. In Xcode, select the FastAPISwarmUI scheme.
2. Click Run (⌘R). A blank window titled “FastAPISwarmUI” appears with a drop zone on top and an empty sidebar below.
3. Open Finder, locate any FastAPI folder (perhaps a simple folder with a `main.py`), and drag it onto the drop zone.
4. Watch the console:
   - The `WorkspaceController.importFastAPIFolder` method copies the folder into `~/FastAPISwarmUI/ManagedApps/<FolderName>/`
   - It then runs `git init` (if no `.git` was present) and makes the initial commit
   - It installs a post-commit hook.
5. Back in the app, you should see a new row under the sidebar with:
   - The folder name
   - “Branch: main” (or “master” depending on your Git defaults)
   - No red dot (since no uncommitted changes)
6. Expand `~/FastAPISwarmUI/ManagedApps/` in Finder; you’ll see `<FolderName>` was copied there, containing a `.git` folder and all your files.

At the end of Sprint 3, you have:
- A working SwiftUI window that accepts folder drops
- A persistent workspace (`~/FastAPISwarmUI/ManagedApps`)
- A sidebar listing all managed apps, with basic Git metadata

—

## Sprint 4 – Service Sidebar ↔ Detail Pane & ClientGen Panel

**Goals**
- Extend `ContentView` into a two-pane `NavigationView`:
  1. Left = Sidebar of Swarm services (driven by the Orchestrator API)
  2. Right = Detail view for a selected service (deploy, logs, config, ClientGen)
- Implement `ServicesViewModel` (fetch list of services)
- Build `ServiceDetailView` (buttons for Deploy, Delete, Logs, Config)
- Build `ClientGenStatusView` (Regenerate + polling)
- Hook everything together so that selecting a ManagedApp shows the corresponding `ServiceDetailView`, merging local Git state with remote Swarm service state

*Note: At this point, each “managed app” in the sidebar maps 1:1 to a Swarm service of the same name. This Sprint assumes you want the sidebar to show not just “local Git projects,” but “Swarm services.” We will blend the two: first show local-managed-folder names, then fetch remote status via API.*

### 4.1 ServicesViewModel.swift

Create `ServicesViewModel.swift` under `Sources/FastAPISwarmUI`:
```swift
import Foundation
import OrchestratorClient
import Combine

/// Fetches and publishes Swarm services from the Orchestrator API.
class ServicesViewModel: ObservableObject {
    @Published var services: [ServiceDetail] = []
    @Published var isLoading = false
    @Published var errorMessage: String? = nil

    private var cancellables = Set<AnyCancellable>()

    /// Load all services via GET /v1/services
    func reloadServices() {
        isLoading = true
        errorMessage = nil

        OrchestratorAPI.shared.listServices { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                switch result {
                case .success(let serviceList):
                    self?.services = serviceList.services
                case .failure(let err):
                    self?.errorMessage = err.localizedDescription
                }
            }
        }
    }

    init() {
        NotificationCenter.default.publisher(for: .serviceDidDeploy)
            .sink { [weak self] _ in
                self?.reloadServices()
            }
            .store(in: &cancellables)
    }
}
```
*Note: We’re calling `OrchestratorAPI.shared.listServices`, which we’ll implement in `OrchestratorAPI.swift` (next step).*

### 4.2 OrchestratorAPI.swift

Create `OrchestratorAPI.swift` under `Sources/FastAPISwarmUI`. This wraps the generated client:
```swift
import Foundation
import OrchestratorClient

/// A singleton wrapper around the generated OrchestratorClient.
class OrchestratorAPI {
    static let shared = OrchestratorAPI()

    let api: DefaultAPI

    private init() {
        let storedBase = UserDefaults.standard.string(forKey: "apiBaseURL") ?? "http://localhost:8000/v1"
        api = DefaultAPI()
        api.apiClient.configuration.basePath = storedBase
    }

    func health(completion: @escaping (Result<HealthResponse, Error>) -> Void) {
        api.healthV1HealthGet { response, error in
            if let err = error {
                completion(.failure(err))
            } else if let resp = response {
                completion(.success(resp))
            } else {
                completion(.failure(NSError(domain: "OrchestratorAPI", code: -1,
                                           userInfo: [NSLocalizedDescriptionKey: "No data"])))
            }
        }
    }

    func listServices(limit: Int = 50,
                      offset: Int = 0,
                      status: String? = nil,
                      completion: @escaping (Result<ServiceListResponse, Error>) -> Void) {
        api.listServicesV1ServicesGet(limit: Int32(limit),
                                      offset: Int32(offset),
                                      status: status) { response, error in
            if let err = error {
                completion(.failure(err))
            } else if let resp = response {
                completion(.success(resp))
            } else {
                completion(.failure(NSError(domain: "OrchestratorAPI", code: -1,
                                           userInfo: [NSLocalizedDescriptionKey: "No data"])))
            }
        }
    }

    func createService(name: String,
                       spec: ServiceSpec,
                       completion: @escaping (Result<ServiceDetail, Error>) -> Void) {
        api.createServiceV1ServicesPost(name: name, serviceSpec: spec) { response, error in
            if let err = error {
                completion(.failure(err))
            } else if let resp = response {
                completion(.success(resp))
            } else {
                completion(.failure(NSError(domain: "OrchestratorAPI", code: -1,
                                           userInfo: [NSLocalizedDescriptionKey: "No data"])))
            }
        }
    }

    func deployService(name: String,
                       completion: @escaping (Result<DeployResponse, Error>) -> Void) {
        api.deployServiceV1ServicesServiceDeployPost(service: name) { response, error in
            if let err = error {
                completion(.failure(err))
            } else if let resp = response {
                NotificationCenter.default.post(name: .serviceDidDeploy, object: name)
                completion(.success(resp))
            } else {
                completion(.failure(NSError(domain: "OrchestratorAPI", code: -1,
                                           userInfo: [NSLocalizedDescriptionKey: "No data"])))
            }
        }
    }

    func deleteService(name: String,
                       completion: @escaping (Result<Void, Error>) -> Void) {
        api.deleteServiceV1ServicesServiceDelete(service: name) { _, error in
            if let err = error {
                completion(.failure(err))
            } else {
                completion(.success(()))
            }
        }
    }

    func getLogs(name: String,
                 tail: Int = 100,
                 completion: @escaping (Result<String, Error>) -> Void) {
        api.getLogsV1ServicesServiceLogsGet(service: name, tail: Int32(tail)) { response, error in
            if let err = error {
                completion(.failure(err))
            } else if let resp = response {
                completion(.success(resp))
            } else {
                completion(.failure(NSError(domain: "OrchestratorAPI", code: -1,
                                           userInfo: [NSLocalizedDescriptionKey: "No data"])))
            }
        }
    }

    func getConfig(name: String,
                   completion: @escaping (Result<ConfigDetail, Error>) -> Void) {
        api.getConfigV1ServicesServiceConfigGet(service: name) { response, error in
            if let err = error {
                completion(.failure(err))
            } else if let resp = response {
                completion(.success(resp))
            } else {
                completion(.failure(NSError(domain: "OrchestratorAPI", code: -1,
                                           userInfo: [NSLocalizedDescriptionKey: "No data"])))
            }
        }
    }

    func patchConfig(name: String,
                     patch: ConfigPatch,
                     completion: @escaping (Result<ConfigDetail, Error>) -> Void) {
        api.patchConfigV1ServicesServiceConfigPatch(service: name, configPatch: patch) { response, error in
            if let err = error {
                completion(.failure(err))
            } else if let resp = response {
                completion(.success(resp))
            } else {
                completion(.failure(NSError(domain: "OrchestratorAPI", code: -1,
                                           userInfo: [NSLocalizedDescriptionKey: "No data"])))
            }
        }
    }

    func rollbackService(name: String,
                         completion: @escaping (Result<DeployResponse, Error>) -> Void) {
        api.rollbackServiceV1ServicesServiceRollbackPost(service: name) { response, error in
            if let err = error {
                completion(.failure(err))
            } else if let resp = response {
                completion(.success(resp))
            } else {
                completion(.failure(NSError(domain: "OrchestratorAPI", code: -1,
                                           userInfo: [NSLocalizedDescriptionKey: "No data"])))
            }
        }
    }

    /// CLIENTGEN
    func regenerateClient(name: String,
                          completion: @escaping (Result<ClientStatusResponse, Error>) -> Void) {
        api.regenerateClientV1ClientgenServiceRegeneratePost(service: name) { response, error in
            if let err = error {
                completion(.failure(err))
            } else if let resp = response {
                completion(.success(resp))
            } else {
                completion(.failure(NSError(domain: "OrchestratorAPI", code: -1,
                                           userInfo: [NSLocalizedDescriptionKey: "No data"])))
            }
        }
    }

    func getClientStatus(name: String,
                         completion: @escaping (Result<ClientStatusResponse, Error>) -> Void) {
        api.getClientStatusV1ClientgenStatusServiceGet(service: name) { response, error in
            if let err = error {
                completion(.failure(err))
            } else if let resp = response {
                completion(.success(resp))
            } else {
                completion(.failure(NSError(domain: "OrchestratorAPI", code: -1,
                                           userInfo: [NSLocalizedDescriptionKey: "No data"])))
            }
        }
    }
}

import Foundation

extension Notification.Name {
    static let serviceDidDeploy = Notification.Name("serviceDidDeploy")
}
```
⏸ **Key points:**
- We set `basePath` from `UserDefaults` (or default to `"http://localhost:8000/v1"`). Adjust if your FastAPI is on a different port.
- Each method wraps a generated endpoint call (e.g. `listServicesV1ServicesGet`) into a Swift-style completion with `Result<,>`.
- The ClientGen methods match your `POST /v1/clientgen/{service}/regenerate` and `GET /v1/clientgen/status/{service}` endpoints.

### 4.3 ServiceRow & ClientGenStatusView

Create `ServiceRow.swift`:
```swift
import SwiftUI

/// A single row showing service name & status color
struct ServiceRow: View {
    let service: ServiceDetail

    var body: some View {
        HStack {
            Text(service.name)
            Spacer()
            Text(service.status)
                .font(.caption)
                .foregroundColor(colorForStatus(service.status))
        }
        .padding(.vertical, 4)
    }

    private func colorForStatus(_ status: String) -> Color {
        switch status.lowercased() {
        case "running":
            return .green
        case "updating":
            return .orange
        case "error":
            return .red
        default:
            return .primary
        }
    }
}
```

Create `ClientGenStatusView.swift`:
```swift
import SwiftUI

/// Shows “Regenerate Client” button + polling for ClientGen status
struct ClientGenStatusView: View {
    let serviceName: String
    @State private var status: String = "unknown"
    @State private var lastGeneratedAt: Date? = nil
    @State private var checksum: String = ""
    @State private var errorMessage: String? = nil
    @State private var isRegenerating: Bool = false

    private let timer = Timer.publish(every: 3, on: .main, in: .common).autoconnect()

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("ClientGen for “\(serviceName)”")
                    .font(.headline)
                Spacer()
                if isRegenerating {
                    ProgressView()
                        .scaleEffect(0.75)
                        .padding(.trailing, 4)
                }
                Button("Regenerate Client") {
                    regenerateClient()
                }
                .disabled(isRegenerating)
            }

            HStack {
                Text("Last Generated At:")
                if let date = lastGeneratedAt {
                    Text(date.formatted(date: .abbreviated, time: .shortened))
                } else {
                    Text("—")
                }
            }
            HStack {
                Text("Checksum:")
                Text(checksum.isEmpty ? "—" : checksum)
                    .font(.system(.body, design: .monospaced))
                    .lineLimit(1)
                    .truncationMode(.middle)
            }
            HStack {
                Text("Status:")
                Text(status.capitalized)
                    .foregroundColor(colorForStatus(status))
            }

            if let err = errorMessage {
                Text("Error: \(err)")
                    .foregroundColor(.red)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding()
        .onAppear {
            fetchStatus()
        }
        .onReceive(timer) { _ in
            if isRegenerating {
                fetchStatus()
            }
        }
    }

    private func regenerateClient() {
        isRegenerating = true
        errorMessage = nil
        OrchestratorAPI.shared.regenerateClient(name: serviceName) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let resp):
                    status = resp.status
                    checksum = resp.checksum
                    lastGeneratedAt = resp.lastGeneratedAt
                case .failure(let err):
                    errorMessage = err.localizedDescription
                    isRegenerating = false
                }
            }
        }
    }

    private func fetchStatus() {
        OrchestratorAPI.shared.getClientStatus(name: serviceName) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let resp):
                    status = resp.status
                    checksum = resp.checksum
                    lastGeneratedAt = resp.lastGeneratedAt
                    if resp.status.lowercased() != "pending" {
                        isRegenerating = false
                        if resp.status.lowercased() == "error", let err = resp.error {
                            errorMessage = err
                        }
                    }
                case .failure(let err):
                    // If 404, maybe service not created; show “n/a”
                    errorMessage = err.localizedDescription
                    isRegenerating = false
                }
            }
        }
    }

    private func colorForStatus(_ status: String) -> Color {
        switch status.lowercased() {
        case "pending":
            return .orange
        case "success":
            return .green
        case "error":
            return .red
        default:
            return .primary
        }
    }
}
```
*Tip: You may need to import `Combine` if you plan to use `AnyCancellable` for more complex polling. For now, `Timer.publish` is enough.*

### 4.4 ConfigEditorView.swift

Create `ConfigEditorView.swift`:
```swift
import SwiftUI

/// Edits a service’s env & ports. Loads via GET, updates via PATCH.
struct ConfigEditorView: View {
    let serviceName: String

    @State private var config: ConfigDetail? = nil
    @State private var portSettings: [String: Int] = [:]
    @State private var envVars: [String: String] = [:]
    @State private var errorMessage: String? = nil

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            if let cfg = config {
                Text("Edit Config for \(serviceName)")
                    .font(.headline)

                Text("Ports:")
                ForEach(Array(portSettings.keys.sorted()), id: \\.self) { key in
                    HStack {
                        Text(key)
                        TextField("Value", value: Binding(
                            get: { portSettings[key] ?? 0 },
                            set: { newVal in portSettings[key] = newVal }
                        ), formatter: NumberFormatter())
                            .frame(width: 60)
                    }
                }

                Text("Env Vars:")
                ForEach(Array(envVars.keys.sorted()), id: \\.self) { key in
                    HStack {
                        Text(key)
                        TextField("Value", text: Binding(
                            get: { envVars[key] ?? "" },
                            set: { newVal in envVars[key] = newVal }
                        ))
                    }
                }

                Button("Save Config") {
                    let patch = ConfigPatch(env: envVars, ports: portSettings)
                    OrchestratorAPI.shared.patchConfig(name: serviceName, patch: patch) { result in
                        DispatchQueue.main.async {
                            switch result {
                            case .success(let updated):
                                config = updated
                                portSettings = updated.ports
                                envVars = updated.env
                            case .failure(let err):
                                errorMessage = err.localizedDescription
                            }
                        }
                    }
                }
                .padding(.top, 8)

                if let err = errorMessage {
                    Text("Error: \(err)")
                        .foregroundColor(.red)
                }
            } else {
                Button("Load Config") {
                    OrchestratorAPI.shared.getConfig(name: serviceName) { result in
                        DispatchQueue.main.async {
                            switch result {
                            case .success(let cfg):
                                config = cfg
                                portSettings = cfg.ports
                                envVars = cfg.env
                            case .failure(let err):
                                errorMessage = err.localizedDescription
                            }
                        }
                    }
                }
            }
        }
        .padding()
        .border(Color.gray)
    }
}
```
*Note: We show a “Load Config” button first; once loaded, we display fields for ports and env.*

### 4.5 ServiceDetailView.swift

Create `ServiceDetailView.swift`:
```swift
import SwiftUI

/// Shows details for one Swarm service: Deploy, Delete, Logs, Config, ClientGen
struct ServiceDetailView: View {
    @State var service: ServiceDetail

    @State private var logs: String = ""
    @State private var showLogs = false
    @State private var showConfigEditor = false
    @State private var isCommitting = false
    @State private var gitErrorMessage: String? = nil

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Service: \(service.name)")
                    .font(.title)
                HStack(spacing: 20) {
                    Text("Status: \(service.status)")
                        .foregroundColor(service.status == "running" ? .green : .red)

                    Spacer()

                    Button("Commit & Deploy") {
                        commitAndDeploy()
                    }
                    .disabled(isCommitting)

                    Button("Delete") {
                        OrchestratorAPI.shared.deleteService(name: service.name) { result in
                            DispatchQueue.main.async {
                                // After deletion, go back to the sidebar
                                // (parent view can observe and remove from list)
                            }
                        }
                    }
                }

                if let err = gitErrorMessage {
                    Text(err)
                        .foregroundColor(.red)
                }

                Divider()

                HStack(spacing: 20) {
                    Button("View Logs") {
                        showLogs.toggle()
                        if showLogs {
                            OrchestratorAPI.shared.getLogs(name: service.name, tail: 200) { result in
                                DispatchQueue.main.async {
                                    switch result {
                                    case .success(let logText):
                                        logs = logText
                                    case .failure(let err):
                                        logs = "Error: \(err.localizedDescription)"
                                    }
                                }
                            }
                        }
                    }

                    Button("Config") {
                        showConfigEditor.toggle()
                    }
                }

                if showLogs {
                    ScrollView {
                        Text(logs)
                            .font(.system(.body, design: .monospaced))
                            .padding()
                    }
                    .frame(maxHeight: 200)
                    .border(Color.gray)
                }

                if showConfigEditor {
                    ConfigEditorView(serviceName: service.name)
                }

                Divider()

                ClientGenStatusView(serviceName: service.name)

                Spacer()
            }
            .padding()
        }
        .onAppear {
            // Optionally refresh service status if you want
        }
    }

    private func commitAndDeploy() {
        guard !isCommitting else { return }
        isCommitting = true
        gitErrorMessage = nil

        // 1. Locate the local folder for this service. We assume workspace.localURL/name
        let workspaceRoot = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("FastAPISwarmUI/ManagedApps", isDirectory: true)
        let localAppURL = workspaceRoot.appendingPathComponent(service.name, isDirectory: true)

        DispatchQueue.global(qos: .userInitiated).async {
            do {
                // 2. Stage & commit all changes
                try GitController.commitAllChanges(in: localAppURL, message: "Auto-commit for \(service.name)")

                // 3. Fire the deploy endpoint
                OrchestratorAPI.shared.deployService(name: service.name) { result in
                    DispatchQueue.main.async {
                        isCommitting = false
                        switch result {
                        case .success:
                            // Optionally reload service status
                            // Here you might send a notification or call a parent view to refresh.
                            print("Deploy succeeded for \(service.name)")
                        case .failure(let err):
                            gitErrorMessage = "Deploy error: \(err.localizedDescription)"
                        }
                    }
                }
            } catch {
                DispatchQueue.main.async {
                    gitErrorMessage = "Git error: \(error.localizedDescription)"
                    isCommitting = false
                }
            }
        }
    }
}
```
**Explanation:**
- “Service: …” heading with **Commit & Deploy** and **Delete** buttons.
- **Commit & Deploy** uses `GitController.commitAllChanges(...)` to stage and commit, then calls `/v1/services/{name}/deploy`.
- Shows errors in red if anything fails.

### 4.6 Putting it all together in ContentView.swift

Update `ContentView.swift` so the left pane shows Swarm services as well as local-managed apps:
```swift
import SwiftUI

struct ContentView: View {
    @StateObject private var workspace = WorkspaceController()
    @StateObject private var servicesVM = ServicesViewModel()
    @State private var selectedService: ServiceDetail?
    @State private var showErrorAlert = false
    @State private var alertMessage = ""

    var body: some View {
        NavigationView {
            VStack {
                // Drag-and-drop zone
                Text("Drop a FastAPI folder here to manage it")
                    .frame(maxWidth: .infinity, minHeight: 80)
                    .padding()
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.gray, lineWidth: 2)
                    )
                    .onDrop(of: [.fileURL], isTargeted: nil, perform: handleDrop(providers:))

                // Local-managed apps list
                List {
                    Section(header: Text("Local FastAPI Projects")) {
                        ForEach(workspace.managedApps) { app in
                            HStack {
                                VStack(alignment: .leading) {
                                    Text(app.name)
                                        .font(.headline)
                                    Text("Branch: \(app.currentBranch)")
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                                Spacer()
                                if app.hasUncommittedChanges {
                                    Circle()
                                        .fill(Color.red)
                                        .frame(width: 10, height: 10)
                                        .help("Uncommitted changes")
                                }
                            }
                        }
                        .onDelete(perform: deleteLocalApps)
                    }

                    Section(header: Text("Swarm Services")) {
                        if servicesVM.isLoading {
                            HStack {
                                Spacer()
                                ProgressView()
                                Spacer()
                            }
                        } else if let error = servicesVM.errorMessage {
                            HStack {
                                Spacer()
                                Text("Error: \(error)")
                                    .foregroundColor(.red)
                                Spacer()
                            }
                        } else {
                            ForEach(servicesVM.services, id: \.name) { svc in
                                NavigationLink(
                                    destination: ServiceDetailView(service: svc),
                                    tag: svc,
                                    selection: $selectedService
                                ) {
                                    ServiceRow(service: svc)
                                }
                            }
                        }
                    }
                }
                .listStyle(SidebarListStyle())
                .frame(minWidth: 250)

                // Refresh button for services
                Button("Refresh Services") {
                    servicesVM.reloadServices()
                }
                .padding(.vertical, 8)
            }

            // Detail pane placeholder
            if let svc = selectedService {
                ServiceDetailView(service: svc)
            } else {
                Text("Select a service to view details")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
        .onAppear {
            servicesVM.reloadServices()
        }
        .alert(isPresented: $showErrorAlert) {
            Alert(title: Text("Error"), message: Text(alertMessage), dismissButton: .default(Text("OK")))
        }
        .frame(minWidth: 900, minHeight: 600)
    }

    private func handleDrop(providers: [NSItemProvider]) -> Bool {
        for provider in providers {
            if provider.hasItemConformingToTypeIdentifier("public.file-url") {
                provider.loadItem(forTypeIdentifier: "public.file-url", options: nil) { (item, error) in
                    DispatchQueue.main.async {
                        guard
                            let data = item as? Data,
                            let url = URL(dataRepresentation: data, relativeTo: nil),
                            url.hasDirectoryPath
                        else {
                            return
                        }
                        workspace.importFastAPIFolder(at: url)
                    }
                }
                return true
            }
        }
        return false
    }

    private func deleteLocalApps(offsets: IndexSet) {
        for index in offsets {
            let app = workspace.managedApps[index]
            workspace.removeManagedApp(app)
        }
    }
}
```
⏸ **Key adjustments:**
- We replaced the earlier sidebar with two Sections inside a single `List`:
  1. Local FastAPI Projects
  2. Swarm Services
- In Swarm Services, we iterate over `servicesVM.services`. Each row is a `NavigationLink` to `ServiceDetailView`.
- Below the `List`, we added a “Refresh Services” button that calls `servicesVM.reloadServices()`.
- On `.onAppear`, we initially call `servicesVM.reloadServices()` so the sidebar populates automatically.
- Added SwiftUI `Alert` for error handling.

—

### 4.7 Run & Verify
1. Build & Run the “FastAPISwarmUI” scheme (⌘R).
2. You should see:
   - A top drop zone
   - A sidebar with two sections: “Local FastAPI Projects” (empty initially) and “Swarm Services” (populated by calling your running FastAPI’s `/v1/services`).
   - A “Refresh Services” button.
3. If your FastAPI backend is running and has some existing Swarm services, they appear in the “Swarm Services” section.
   - Each row shows `service.name` and `service.status` (colored).
   - Clicking a row navigates to the detail pane on the right.
4. Test Local Drag-and-Drop again: drag a folder into the drop zone → it shows up under “Local FastAPI Projects.” Check that Git folders were created under `~/FastAPISwarmUI/ManagedApps/`.

At the end of Sprint 4, you have:
- A two-pane SwiftUI app:
  1. Left = Lists both local-managed FastAPI projects and remote Swarm services
  2. Right = Detail view with Deploy, Delete, Logs, Config, and ClientGen

—

## Sprint 5 – Advanced Features & Polish

**Goals**
1. “Commit & Deploy” button inside `ServiceDetailView` that stages, commits, and triggers Orchestrator API
2. Auto-refresh Git status & Swarm status after actions
3. Fine-tune error handling (e.g. show alerts on API or Git errors)
4. Preferences: let user configure API base URL, workspace location, auto-deploy toggle

### 5.1 Add “Commit & Deploy” in ServiceDetailView

Open `ServiceDetailView.swift` and modify the button area at the top—replace:
```swift
HStack {
    Text("Status: \(service.status)")
        .foregroundColor(service.status == "running" ? .green : .red)
    Spacer()
    Button("Deploy") {
        OrchestratorAPI.shared.deployService(name: service.name) { result in
            DispatchQueue.main.async {
                // You could refresh status after deploy
            }
        }
    }
    Button("Delete") {
        OrchestratorAPI.shared.deleteService(name: service.name) { result in
            DispatchQueue.main.async {
                // Handle UI change (e.g. dismiss detail view)
            }
        }
    }
}
```
with:
```swift
HStack(spacing: 20) {
    Text("Status: \(service.status)")
        .foregroundColor(service.status == "running" ? .green : .red)

    Spacer()

    Button("Commit & Deploy") {
        commitAndDeploy()
    }

    Button("Delete") {
        OrchestratorAPI.shared.deleteService(name: service.name) { result in
            DispatchQueue.main.async {
                // After deletion, go back to the sidebar
                // (parent view can observe and remove from list)
            }
        }
    }
}
```

Below the `body`, add these state & helper methods:
```swift
@State private var isCommitting = false
@State private var gitErrorMessage: String? = nil

private func commitAndDeploy() {
    guard !isCommitting else { return }
    isCommitting = true
    gitErrorMessage = nil

    // 1. Locate the local folder for this service. We assume workspace.localURL/name
    let workspaceRoot = FileManager.default.homeDirectoryForCurrentUser
        .appendingPathComponent("FastAPISwarmUI/ManagedApps", isDirectory: true)
    let localAppURL = workspaceRoot.appendingPathComponent(service.name, isDirectory: true)

    DispatchQueue.global(qos: .userInitiated).async {
        do {
            // 2. Stage & commit all changes
            try GitController.commitAllChanges(in: localAppURL, message: "Auto-commit for \(service.name)")

            // 3. Fire the deploy endpoint
            OrchestratorAPI.shared.deployService(name: service.name) { result in
                DispatchQueue.main.async {
                    isCommitting = false
                    switch result {
                    case .success:
                        // Optionally reload service status
                        // Here you might send a notification or call a parent view to refresh.
                        print("Deploy succeeded for \(service.name)")
                    case .failure(let err):
                        gitErrorMessage = "Deploy error: \(err.localizedDescription)"
                    }
                }
            }
        } catch {
            DispatchQueue.main.async {
                gitErrorMessage = "Git error: \(error.localizedDescription)"
                isCommitting = false
            }
        }
    }
}
```

Below that, just above `Spacer()`, show potential Git errors:
```swift
if let err = gitErrorMessage {
    Text(err)
        .foregroundColor(.red)
}
```

Now you have a **Commit & Deploy** button that:
1. Uses `GitController.commitAllChanges(...)` to stage and commit
2. Fires off `OrchestratorAPI.shared.deployService(name:)` asynchronously
3. Shows errors in red if anything fails

### 5.2 Auto-refresh after actions
- After commit & deploy, you may want to refresh both Git status and the remote service list. The simplest approach is for the parent view to observe notifications:

In `OrchestratorAPI.swift`, after a successful deploy, post a notification:
```swift
func deployService(name: String,
                   completion: @escaping (Result<DeployResponse, Error>) -> Void) {
    api.deployServiceV1ServicesServiceDeployPost(service: name) { response, error in
        if let err = error {
            completion(.failure(err))
        } else if let resp = response {
            // Notify others that a deploy occurred
            NotificationCenter.default.post(name: .serviceDidDeploy, object: name)
            completion(.success(resp))
        } else {
            completion(.failure(NSError(domain: "OrchestratorAPI", code: -1,
                                       userInfo: [NSLocalizedDescriptionKey: "No data"])))
        }
    }
}
```
Ensure you have:
```swift
extension Notification.Name {
    static let serviceDidDeploy = Notification.Name("serviceDidDeploy")
}
```

In `ServicesViewModel.swift`, listen for that notification to reload services:
```swift
init() {
    NotificationCenter.default.publisher(for: .serviceDidDeploy)
        .sink { [weak self] _ in
            self?.reloadServices()
        }
        .store(in: &cancellables)
}
```

Likewise, after a successful Git commit (inside `commitAndDeploy()`), you could post:
```swift
NotificationCenter.default.post(name: .gitDidCommit, object: service.name)
```
and have `WorkspaceController` or the main view listen to update local status. For brevity, we’ll skip that, assuming the user manually refreshes or the next `scanWorkspace()` happens on app launch.

### 5.3 Show SwiftUI Alerts for Errors

In `ContentView.swift`, add:
```swift
@State private var showErrorAlert = false
@State private var alertMessage = ""
```
Wherever you detect an error (e.g. in `servicesVM.reloadServices()` completion), set:
```swift
DispatchQueue.main.async {
    self.alertMessage = err.localizedDescription
    self.showErrorAlert = true
}
```

Then modify the view to include:
```swift
.alert(isPresented: $showErrorAlert) {
    Alert(title: Text("Error"), message: Text(alertMessage), dismissButton: .default(Text("OK")))
}
```

You can replicate similar error-alert logic inside `ServiceDetailView` for Git errors or API errors by adding `@State private var showDetailError = false` and showing an `Alert`.

### 5.4 Preferences: API URL & Workspace Location

(Optional but recommended for polish.)

Create a new file `SettingsView.swift` under `Sources/FastAPISwarmUI`:
```swift
import SwiftUI

struct SettingsView: View {
    @AppStorage("apiBaseURL") private var apiBaseURL: String = "http://localhost:8000/v1"
    @AppStorage("workspacePath") private var workspacePath: String = NSHomeDirectory() + "/FastAPISwarmUI/ManagedApps"
    @AppStorage("autoDeployOnCommit") private var autoDeployOnCommit: Bool = true

    var body: some View {
        Form {
            Section(header: Text("API Settings")) {
                TextField("Orchestrator Base URL", text: $apiBaseURL)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
            }

            Section(header: Text("Workspace")) {
                TextField("Workspace Folder", text: $workspacePath)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
            }

            Section {
                Toggle("Auto-deploy on Git commit", isOn: $autoDeployOnCommit)
            }
        }
        .padding()
        .frame(width: 400)
    }
}
```

In `OrchestratorAPI.swift`, change `basePath` to read from `AppStorage`:
```swift
private init() {
    let storedBase = UserDefaults.standard.string(forKey: "apiBaseURL") ?? "http://localhost:8000/v1"
    api = DefaultAPI()
    api.apiClient.configuration.basePath = storedBase
}
```

Similarly, in `WorkspaceController`, read the workspace folder from `UserDefaults`:
```swift
init() {
    let defaultWorkspace = NSHomeDirectory() + "/FastAPISwarmUI/ManagedApps"
    let path = UserDefaults.standard.string(forKey: "workspacePath") ?? defaultWorkspace
    let url = URL(fileURLWithPath: path, isDirectory: true)
    workspaceRoot = url

    try? FileManager.default.createDirectory(at: workspaceRoot, withIntermediateDirectories: true, attributes: nil)
    scanWorkspace()
}
```

Finally, in your `FastAPISwarmUIApp.swift`, add a Settings pane:
```swift
import SwiftUI

@main
struct FastAPISwarmUIApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        Settings {
            SettingsView()
        }
    }
}
```
Now when you run, you get a standard macOS Preferences window from the app menu, letting users change the API URL, workspace path, and auto-deploy toggle.

> _Tip:_ After editing Preferences, you may need to rebuild or restart the app so that `OrchestratorAPI.shared` picks up new settings. For production polish, you could observe `UserDefaults.didChangeNotification` and reconfigure `api.apiClient.configuration.basePath` on the fly.

At the end of Sprint 5, you have:
- A “Commit & Deploy” flow that stages, commits, and calls your FastAPI endpoint `/v1/services/{name}/deploy`
- Automatic refresh of the Swarm service list after deploy
- SwiftUI Alerts for errors
- A Preferences window for base URL, workspace folder, and auto-deploy toggle

—

## Sprint 6 – Final Polishing & Packaging

**Goals**
1. Clean up UI (icons, spacing, colors)
2. Provide an “About” dialog with version info
3. Ensure the post-commit hook respects “auto-deploy on commit” Preferences toggle
4. Code signing & sandboxing (if you want to distribute outside your machine)

### 6.1 Respect “Auto-deploy on commit” in Git hook

Modify `GitController.installGitHooks(at:)` to check `autoDeployOnCommit`:
```swift
static func installGitHooks(at folder: URL) {
    let autoDeploy = UserDefaults.standard.bool(forKey: "autoDeployOnCommit")
    let hooksDir = folder.appendingPathComponent(".git/hooks", isDirectory: true)
    do {
        try FileManager.default.createDirectory(at: hooksDir, withIntermediateDirectories: true, attributes: nil)

        let projectName = folder.lastPathComponent
        var hookScript = """
        #!/bin/sh
        # post-commit hook: after each commit, optionally notify FastAPI Orchestrator
        PROJECT_NAME="\(projectName)"
        COMMIT_SHA=$(git rev-parse HEAD)
        """

        if autoDeploy {
            hookScript += """

            curl -X POST \\
              "http://localhost:8000/v1/services/\(projectName)/deploy" \\
              -H "Content-Type: application/json"
            """
        } else {
            hookScript += "\n# autoDeployOnCommit == false, so skipping deploy\n"
        }

        let hookURL = hooksDir.appendingPathComponent("post-commit")
        try hookScript.write(to: hookURL, atomically: true, encoding: .utf8)

        var attributes = try FileManager.default.attributesOfItem(atPath: hookURL.path)
        attributes[.posixPermissions] = 0o755
        try FileManager.default.setAttributes(attributes, ofItemAtPath: hookURL.path)
    } catch {
        print("Failed to install Git hook: \(error)")
    }
}
```
Now if the user toggles off Auto-deploy on Git commit, the hook writes a no-op script (only a comment). If they toggle it on again, you’ll need to re-install hooks (either manually delete and re-drop, or add a “Refresh Hooks” command in the UI). For simplicity, you can advise users to re-import their folder if they change that setting.

### 6.2 “About” Dialog

In `FastAPISwarmUIApp.swift`, add an `AboutDialogView`:
```swift
import SwiftUI

struct AboutDialogView: View {
    var body: some View {
        VStack(alignment: .center, spacing: 8) {
            Text("FastAPI Swarm UI")
                .font(.title)
            Text("Version 1.0.0")
                .font(.subheadline)
            Divider()
            Text("A macOS app to manage FastAPI services on Docker Swarm.\nBuilt with SwiftUI & FastAPI.")
                .multilineTextAlignment(.center)
            Spacer()
        }
        .padding()
        .frame(width: 300, height: 200)
    }
}
```

Then modify the App struct to present it via a menu command:
```swift
import SwiftUI
import Cocoa

@main
struct FastAPISwarmUIApp: App {
    @State private var showingAbout = false

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        Settings {
            SettingsView()
        }
        .commands {
            CommandGroup(replacing: .appInfo) {
                Button("About FastAPI Swarm UI") {
                    showingAbout = true
                }
                .keyboardShortcut("i", modifiers: .command)
            }
        }
        .sheet(isPresented: $showingAbout) {
            AboutDialogView()
        }
    }
}
```
Now under the App menu, “About FastAPI Swarm UI” appears (⌘I) opening a simple About dialog.

### 6.3 Basic UI Polish
- **Icons:** Add an app icon set. In Xcode, under `Assets.xcassets`, create an AppIcon set and drag in 128×128, 256×256, 512×512 PNGs.
- **Spacing & Fonts:** Scan through each SwiftUI view (`ContentView`, `ServiceDetailView`, etc.) and ensure there’s consistent padding (e.g. `.padding()` on major `VStack`s) and readable fonts.
- **Colors:** Use system colors (e.g. `Color.accentColor`) rather than hardcoded ones where possible.

### 6.4 Code-Signing & Sandboxing (Optional)

If you want to distribute outside your development machine (e.g. to teammates):
1. In Xcode, select FastAPISwarmUI target → Signing & Capabilities → check “Automatically manage signing” → choose your Team.
2. To enable sandboxing (more restrictive), click “+ Capability” → “App Sandbox.” By default, your drag-and-drop and file-reading from `~/FastAPISwarmUI/ManagedApps` requires “User Selected File” rights. Under “App Sandbox,” check “User Selected File” → “Read/Write.”
3. For network calls to `localhost:8000`, under App Sandbox → “Outbound Connections (Client)” → Check.
4. Build & Run. If errors appear about file access, revise sandbox settings to allow “Temporary exception for ENTITLEMENTS.” For internal distribution, you may skip sandboxing entirely.

### 6.5 Archive & Export
1. In Xcode, set the build scheme to Release.
2. Product → Clean Build Folder (⇧⌘K).
3. Product → Archive.
4. In the Organizer window, click Distribute App.
   - If you want to share a simple .app (not via Mac App Store), choose “Copy Mac OS Application” and export to a location.
   - This yields `FastAPISwarmUI.app` that you can zip and send to colleagues.

At the end of Sprint 6, you have a fully-polished, copy-and-paste-ready macOS SwiftUI application:
- Preferences to configure API URL, workspace path, and auto-deploy toggle
- Left sidebar with Local FastAPI Projects + Swarm Services
- Detail pane for Deploy, Delete, Logs, Config, and ClientGen
- “Commit & Deploy” button that stages commits and calls your FastAPI
- About dialog and code signing ready (optional)

—

## Final Checklist & Folder Structure

By the end of these sprints, your `~/FastAPISwarmUI` should resemble:

```
FastAPISwarmUI/
├── Package.swift
├── orchestrator-openapi.json
├── GeneratedOrchestratorClient/        ← can be removed or kept for regeneration
│   └── Sources/OrchestratorClient/…
└── Sources/
    ├── FastAPISwarmUI/
    │   ├── AboutDialogView.swift
    │   ├── ClientGenStatusView.swift
    │   ├── ConfigEditorView.swift
    │   ├── ContentView.swift
    │   ├── FastAPISwarmUIApp.swift
    │   ├── GitController.swift
    │   ├── OrchestratorAPI.swift
    │   ├── ServicesViewModel.swift
    │   ├── ServiceDetailView.swift
    │   ├── ServiceRow.swift
    │   ├── SettingsView.swift
    │   └── WorkspaceController.swift
    └── OrchestratorClient/            ← generated code from Sprint 1
        ├── APIs/
        ├── Models/
        └── Package.swift
```

**Running the App**
1. Start your FastAPI Swarm Orchestrator on `localhost:8000` (e.g. `uvicorn main:app --host 0.0.0.0 --port 8000`).
2. Run the App in Xcode (⌘R) or double-click the exported `.app`.
3. Use the Preferences (⌘,) to point to a different base URL (if needed) or change your workspace folder.
4. Drag a FastAPI project folder into the drop zone.
5. Select a service under “Swarm Services” to view details, commit changes, deploy, or regenerate client code.

—

**Congratulations!**

You now have full end-to-end instructions—organized as 6 sprints—for building a macOS SwiftUI application that:
- Manages FastAPI code under Git
- Integrates tightly with your Swarm Orchestrator API
- Provides local-project & Swarm-service overviews
- Allows Deploy, Delete, Logs, Config, and ClientGen actions
- Respects user preferences for workspace location, API URL, and auto-deploy
- Is signed and ready for distribution

Feel free to revisit any sprint if you need additional tweaks or to regenerate your client after evolving your FastAPI backend. Happy coding!
