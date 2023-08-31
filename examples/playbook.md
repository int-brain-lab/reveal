
`aws --profile ibl s3 sync ~/Documents/JS/reveal.js s3://reveal.internationalbrainlab.org --exclude reveal.js/node_modules`
http://reveal.internationalbrainlab.org.s3-website-us-east-1.amazonaws.com


## clone a new repository

```shell

dirname=critical
git clone https://github.com/oliche/reveal.js.git -b ibl $dirname
cd $dirname
ln -s ../reveal.js/node_modules node_modules
mkdir img
cp index_template.html index.html
npm install
```

## run a local server
`npm start -- --port=8001`

## update the bucket
aws --profile ibl s3 sync ~/Documents/JS/reveal.js s3://reveal.internationalbrainlab.org --delete --exclude reveal.js/node_modules

## Create a new website
```shell
dirname='critical'
bucket=$dirname.internationalbrainlab.org
aws --profile ibl s3api create-bucket --bucket=$bucket --acl=public-read
aws --profile ibl s3 website s3://$bucket/ --index-document index.html

echo '{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::'$bucket'/*"
        }
    ]
}' > /tmp/bucket_policy.json
aws --profile ibl s3api put-bucket-policy --bucket $bucket --policy file:///tmp/bucket_policy.json
aws --profile ibl s3 sync ~/Documents/JS/$dirname s3://$bucket

echo http://$bucket.s3-website-us-east-1.amazonaws.com
```

## Update a website
```shell
bucket=reveal.internationalbrainlab.org
aws --profile ibl s3 sync ~/Documents/JS/reveal s3://reveal.internationalbrainlab.org --delete
echo http://$bucket.s3-website-us-east-1.amazonaws.com --exclude reveal.js/node_modules`
```


