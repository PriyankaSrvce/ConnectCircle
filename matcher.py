#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#define MAX 50
#define INF 99999

// ---------------- GRAPH STRUCTURES -----------------

typedef struct Node {
    int v;
    int w;                 // weight (distance)
    struct Node* next;
} Node;

Node* graph[MAX]; // adjacency list
int n = 0;        // total nodes

// ---------------- VOLUNTEER DATA --------------------

int isVolunteer[MAX];
int available[MAX];
int trust[MAX];

// ---------------- QUEUE FOR BFS ---------------------

int queue[MAX];
int front = -1, rear = -1;

void enqueue(int x){
    if(rear == MAX-1) return;
    if(front == -1) front = 0;
    queue[++rear] = x;
}

int dequeue(){
    if(front == -1) return -1;
    int x = queue[front++];
    if(front > rear){ front = rear = -1; }
    return x;
}

int isEmpty(){
    return front == -1;
}

// ---------------- ADD EDGE ---------------------

void addEdge(int u, int v, int w){
    Node* temp = (Node*)malloc(sizeof(Node));
    temp->v = v;
    temp->w = w;
    temp->next = graph[u];
    graph[u] = temp;

    temp = (Node*)malloc(sizeof(Node));
    temp->v = u;
    temp->w = w;
    temp->next = graph[v];
    graph[v] = temp;
}

// ---------------- PRINT GRAPH -------------------------

void printGraph(){
    printf("\nCommunity Graph (Adjacency List):\n");
    for(int i=0;i<n;i++){
        printf("%d -> ", i);
        Node* temp = graph[i];
        while(temp){
            printf("%d(%d) ", temp->v, temp->w);
            temp = temp->next;
        }
        printf("\n");
    }
}

// ---------------- BFS (UNWEIGHTED) ---------------------

void bfs(int src, int dist[]){
    for(int i=0;i<n;i++) dist[i] = INF;

    dist[src] = 0;
    enqueue(src);

    while(!isEmpty()){
        int u = dequeue();
        Node* temp = graph[u];

        while(temp){
            int v = temp->v;
            if(dist[v] == INF){
                dist[v] = dist[u] + 1;
                enqueue(v);
            }
            temp = temp->next;
        }
    }
}

// ---------------- DIJKSTRA (WEIGHTED) ---------------------

void dijkstra(int src, int dist[]){
    int vis[MAX]={0};

    for(int i=0;i<n;i++) dist[i]=INF;
    dist[src]=0;

    for(int count=0; count<n-1; count++){
        int u=-1;

        for(int i=0;i<n;i++)
            if(!vis[i] && (u==-1 || dist[i]<dist[u]))
                u=i;

        vis[u]=1;

        Node* temp=graph[u];
        while(temp){
            int v=temp->v;
            int w=temp->w;
            if(dist[u]+w < dist[v]){
                dist[v]=dist[u]+w;
            }
            temp=temp->next;
        }
    }
}

// ---------------- TRUST UPDATE ---------------------

void updateTrust(int vol, int delta){
    trust[vol] += delta;
    if(trust[vol] < 0) trust[vol] = 0;
    if(trust[vol] > 10) trust[vol] = 10;
}

// ---------------- AVAILABILITY UPDATE ---------------------

void setAvailability(int vol, int status){
    available[vol] = status;
}

// ---------------- MATCHING FUNCTION ---------------------

int matchVolunteer(int requester, int weighted){

    int dist[MAX];

    if(weighted)
        dijkstra(requester, dist);
    else
        bfs(requester, dist);

    int bestVol = -1;
    int bestScore = -INF;

    for(int i=0;i<n;i++){
        if(isVolunteer[i] && available[i] && dist[i]!=INF){

            int score = trust[i]*10 - dist[i];

            if(score > bestScore){
                bestScore = score;
                bestVol = i;
            }
        }
    }

    return bestVol;
}

// ---------------- MAIN DEMO ---------------------

int main(){

    n = 8; // nodes 0..7

    // build graph (weights = distance between areas)
    addEdge(0,1,1);
    addEdge(1,2,1);
    addEdge(2,3,1);
    addEdge(3,4,2);
    addEdge(1,5,1);
    addEdge(5,6,1);
    addEdge(6,7,1);

    printGraph();

    // mark volunteers
    isVolunteer[3]=1;
    isVolunteer[5]=1;
    isVolunteer[7]=1;

    // availability
    available[3]=1;
    available[5]=1;
    available[7]=1;

    // trust (0–10)
    trust[3]=5;
    trust[5]=8;
    trust[7]=6;

    int requester = 0;

    printf("\nRequester: %d\n", requester);

    int volunteer = matchVolunteer(requester, 0); // 0 = BFS mode

    if(volunteer==-1){
        printf("No volunteer available.\n");
        return 0;
    }

    printf("\nBest volunteer assigned: %d\n", volunteer);

    printf("\nVolunteer %d rejected.\n", volunteer);
    setAvailability(volunteer, 0);
    updateTrust(volunteer, -1);

    int second = matchVolunteer(requester, 0);

    if(second==-1)
        printf("\nNo fallback volunteer available.\n");
    else
        printf("\nFallback volunteer assigned: %d\n", second);

    printf("\nTrust Scores after update:\n");
    for(int i=0;i<n;i++){
        if(isVolunteer[i])
            printf("Volunteer %d -> Trust %d\n", i, trust[i]);
    }

    return 0;
}
