library(ggplot2)
library(OpenImageR)
library(bmp)
library(e1071)
library(pracma)

#We turn all the pictures into data we can work with
{
names = list.files(pattern = "jpg")
data = matrix(0, length(names),108000)
for (i in 1:length(names)){
  Im = readImage(names[i])
  red = as.vector(Im[,,1])
  green = as.vector(Im[,,2])
  blue = as.vector(Im[,,3])
  data[i,] = t(c(red, green, blue))
  }
}

#First of all we are going to perform the PCA in the original data
#so we can use the FDA in reduced version of the data. We cannot  
#perform FDA inoriginal data because it is too large.
{
Eigen_PCA=function(data,var){
  data.scaled=scale(data,center=T,scale=T)
  Sigma_ = data.scaled%*%t(data)/(nrow(data.scaled)-1)
  Eigen = eigen(Sigma_)
  Eigenvalues = Eigen$values
  Cummulative.Var = cumsum(Eigenvalues)/sum(Eigenvalues)
  VarLim=min(which(Cummulative.Var>var))
  Eigenvectors = Eigen$vectors[,1:VarLim]
  Eigenfaces = t(data.scaled)%*%Eigenvectors
  return(Eigenfaces)
}

Eigenfaces=Eigen_PCA(data,0.95)
data.scaled=scale(data,center=T,scale=T)
data_new=data.scaled%*%Eigenfaces





}


#The FDA function
FDA=function(data_new){
  m=colMeans(data_new)
  colMeans(data_new[1:6,])
  sec=seq(1,150,6)
  Ms=matrix(0,25,ncol(data_new))
  index=0
  for (i in sec){
    index=index+1
    Ms[index,]=colMeans(data_new[i:(i+5),])
  }
  
  SW=matrix(0,ncol(data_new),ncol(data_new))
  for (i in 1:150){
    SW=SW+as.matrix(data_new[i,]-Ms[floor((i-1)/6+1),])%*%t(data_new[i,]-Ms[floor((i-1)/6+1),])
  }
  SB=matrix(0,ncol(data_new),ncol(data_new))
  for (i in 1:25){
    SB=SB+6*(Ms[i,]-m)%*%t(Ms[i,]-m)
  }
  eig = eigen(solve(SW)%*%SB)
  P = Re(eig$vectors)
  D = Re(eig$values)
  FDA=list(m,P,D)
  return(FDA)
}

#This function takes as an input a set of variables, it performs the 
#FDA in those observations and then calculates the final data we are 
#going to use to perform our predictions depending of the variance
#explained by the chosen vectors.
Eigen_FDA=function(data_new,var){
  fisher=FDA(data_new)
  eigenvalues=fisher[[3]]
  eigenvector=fisher[[2]]
  prop.var = eigenvalues/sum(eigenvalues)
  cummulative.var = cumsum(eigenvalues/sum(eigenvalues))
  VarLim=min(which(cummulative.var>var))
  Eigenfaces = eigenvector[,1:VarLim]
}

#Here we create our knn function and check how long it takes the program
#to perform a single prediction for random chosen train and test sets.
{

a=NULL
for (i in 1:25){
  a=c(a,rep(i,6))
}

my_knn_ = function(train,test,Eigenfaces_PCA,Eigenfaces_FDA,method,k){
  train = t(t(Eigenfaces_PCA)%*%t(train))
  test = t(t(Eigenfaces_PCA)%*%test)
  train = t(t(Eigenfaces_FDA)%*%t(train))
  test = t(t(Eigenfaces_FDA)%*%t(test))
  temp=NULL
  minimum = NULL
  for (i in 1:nrow(train)){
    x = rbind(test,train[i,])
    temp = c(temp, as.numeric(dist(x, method = method)))
  }
  b=a[sort(temp, index.return = TRUE)$ix[1:k]]
  temp1 <- table(as.vector(b))
  return(as.numeric(names(temp1)[temp1 == max(temp1)]))}

var=0.95
Eigenfaces_PCA=Eigen_PCA(data,var)
Eigenfaces_FDA=Eigen_FDA(data_new,var)



tic()
num=sample(1:150,1)
train = data[-num,]
test = data[num,]
my_knn_(train,test,Eigenfaces_PCA,Eigenfaces_FDA,"canberra",3)
a[num]
toc()

}



#From this point on we will try to find  the best parameters to use 
#in our final function

#1: Methods
{
k=5
methods=c("euclidean", "maximum", "manhattan", "canberra")
chek.matrix=matrix(0,4,1)
rownames(chek.matrix)=methods


var=0.95
Eigenfaces_PCA=Eigen_PCA(data,var)
Eigenfaces_FDA=Eigen_FDA(data_new,var)


n.rep=20
preds=rep(0,n.rep)
real=rep(0,n.rep)


for (i in 1:4){
    for (n in 1:n.rep){
      num=sample(1:150,1)
      train = data[-num,]
      test = data[num,]
      temp=my_knn_(train,test,Eigenfaces_PCA,Eigenfaces_FDA,methods[i],k)
      preds[n]=temp
      real[n]=a[num]
    }
    accuracy=length(which((preds==real)=="TRUE"))/n.rep
    chek.matrix[i,]=accuracy
  }



chek.matrix
View(chek.matrix)

}

#2: Value of K
{
  
ks=seq(1,9,2)
chek.ks=matrix(2,length(ks),2)
chek.ks[,1]=ks
colnames(chek.ks)=c("k","acc")

n.rep=20
preds=rep(0,n.rep)
real=rep(0,n.rep)

for (i in 1:length(ks)){
  for (l in 1:n.rep){
    num=sample(1:150,1)
    train = data_new[-num,]
    test = data_new[num,]
    temp = my_knn_(train,test,Eigenfaces_PCA,Eigenfaces_FDA,"canberra",ks[i])
    preds[l]=temp
    real[l]=a[num]
  }
  accuracy=length(which((preds==real)=="TRUE"))/n.rep
  chek.ks[i,2]=accuracy
}
chek.ks
View(chek.ks)

}

#3: Computing the Threshold
{


  

data_th = data.scaled%*%Eigenfaces_PCA
data_th = data_th%*%Eigenfaces_FDA


my_knn_all= function(train){
  distance_matrix = matrix(0, nrow(train), nrow(train))
  for (i in 1:nrow(train)){
    temp = NULL
    for (j in 1:nrow(train)){
      x = rbind(train[i,],train[j,])
      temp = as.numeric(dist(x, method = "canberra"))
      distance_matrix[i,j] = temp
    }
  }
  return (as.vector(distance_matrix[distance_matrix>0]))}
#With this function we calculate all the distances and keep them in a vector

values = my_knn_all(data_th)

df_values1 = as.data.frame(values)
ggplot(data= df_values1, aes(x = values))+
  geom_histogram(bins = 60)+xlab("Values")+ylab("")+labs(title = "All distances")



max(values)
min(values)

threshold = seq(0, 14, 0.01)

matrix.pred = matrix(0, length(threshold), 3)
colnames(matrix.pred) = c("Threshold", "Real", "Impostor")

matrix.pred[,1] = threshold

for (i in values){
  for (j in 1:length(threshold)){
    if (i < threshold[j]){
      matrix.pred[j,2] = (matrix.pred[j,2] + 1)
    }
    else{
      matrix.pred[j,3] = (matrix.pred[j,3] + 1)
    }
  } 
}

View(matrix.pred)

data1 = as.data.frame(matrix.pred)

ggplot(data1)+aes(x = data1$Threshold, y = data1$Real) +
  geom_line(color = "green")+
  geom_line(aes(x = data1$Threshold, y = data1$Impostor), color = "red")+
  xlab("Threshold") + ylab(NULL) 


reales = data_th[1:125,]
impostores = data_th[126:150,]
real.impostors = rep.int(c(0,1), times = c(125, 25))
n.reales=125*124
n.impostores=25*24


ftr_=NULL
tfr_=NULL

x = my_knn_all(reales)
y = my_knn_all(impostores)
for (i in threshold){
  pred.real = (x > i)+0
  pred.impostors = (y > i)+0
  tfr = sum(pred.real == 1)/n.reales
  tfr_ = c(tfr_, tfr)
  
  ftr = sum(pred.impostors == 0)/n.impostores
  ftr_ = c(ftr_, ftr)
}


ggplot()+
  geom_line(aes(x = threshold, y = tfr_),color = "red")+
  geom_line(aes(x = threshold, y = ftr_),color = "green")+
  ylab("")


x=tfr_>ftr_
intercept=threshold[which(diff(x)!=0)]

}



#Once we have decided which parameters we are going to use, we create our final
#function and check how well it is working for the given dataset.
{

final_knn_ = function(train, test,Eigenfaces_PCA,Eigenfaces_FDA,method,k,threshold){
  train = t(t(Eigenfaces_PCA)%*%t(train))
  test = t(t(Eigenfaces_PCA)%*%test)
  train = t(t(Eigenfaces_FDA)%*%t(train))
  test = t(t(Eigenfaces_FDA)%*%t(test))
  temp=NULL
  for (i in 1:nrow(train)){
    x = rbind(test,train[i,])
    d = as.numeric(dist(x, method = method))
    if (d>threshold){
      d=Inf
    }
    temp = c(temp, d)
  }
  b=a[sort(temp, index.return = TRUE)$ix[1:k]]
  c=sort(temp)[1:5]
  temp1 <- table(as.vector(b))
  temp2 <- table(as.vector(c))
  if (as.numeric(names(temp2)[temp2 == max(temp2)])==Inf){
    return(0)
  }
  return(as.numeric(names(temp1)[temp1 == max(temp1)]))}

n.rep=50
preds=rep(0,n.rep)
real=rep(0,n.rep)

for (l in 1:n.rep){
  num=sample(1:150,1)
  train = data[-num,]
  test = data[num,]
  temp = final_knn_(train,test,Eigenfaces_PCA,Eigenfaces_FDA,"canberra",5,10.36)
  preds[l]=temp
  real[l]=a[num]
}


preds
real
accuracy=length(which((preds==real)=="TRUE"))/n.rep

}

